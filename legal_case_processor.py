#!/usr/bin/env python3
"""
Legal Case Processing Agent

This agent processes forwarded emails containing legal case information,
extracts data from PDFs and email content, performs underwriting analysis,
and provides comprehensive case summaries with risk analysis.

Pipeline:
1. PDF Parsing & Underwriting Summary
2. Underwriting Gaps & Follow-Up Questions  
3. External Data Enrichment (Location Analysis, Attorney Verification)
4. Comprehensive Reply Generation
"""

import os
import re
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.google import Gemini
from email_pdf_agent import EmailPDFAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('legal_case_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CaseData:
    """Structure for extracted case data"""
    client_name: Optional[str] = None
    date_of_loss: Optional[str] = None
    accident_type: Optional[str] = None
    injuries: List[str] = None
    treatment: List[str] = None
    medical_providers: List[str] = None
    insurance_info: Optional[str] = None
    policy_limits: Optional[str] = None
    liability_info: Optional[str] = None
    attorney_name: Optional[str] = None
    attorney_email: Optional[str] = None
    law_firm: Optional[str] = None
    accident_location: Optional[str] = None
    
    def __post_init__(self):
        if self.injuries is None:
            self.injuries = []
        if self.treatment is None:
            self.treatment = []
        if self.medical_providers is None:
            self.medical_providers = []

@dataclass
class LocationAnalysis:
    """Structure for location risk analysis"""
    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    political_leaning: Optional[str] = None
    tort_environment: Optional[str] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class AttorneyVerification:
    """Structure for attorney verification data"""
    name: Optional[str] = None
    bar_status: Optional[str] = None
    license_number: Optional[str] = None
    state: Optional[str] = None
    email_verified: bool = False
    firm_verified: bool = False
    notes: Optional[str] = None

@dataclass
class PoliceReportData:
    """Structure for extracted police report data"""
    report_number: Optional[str] = None
    report_date: Optional[str] = None
    incident_date: Optional[str] = None
    incident_time: Optional[str] = None
    location: Optional[str] = None
    officers: List[str] = None
    parties_involved: List[str] = None
    vehicles: List[str] = None
    violations: List[str] = None
    narrative: Optional[str] = None
    weather_conditions: Optional[str] = None
    road_conditions: Optional[str] = None
    traffic_control: Optional[str] = None
    damage_assessment: Optional[str] = None
    injuries_reported: List[str] = None
    fault_determination: Optional[str] = None
    witness_statements: List[str] = None
    citations_issued: List[str] = None
    towed_vehicles: List[str] = None
    property_damage: Optional[str] = None
    
    def __post_init__(self):
        if self.officers is None:
            self.officers = []
        if self.parties_involved is None:
            self.parties_involved = []
        if self.vehicles is None:
            self.vehicles = []
        if self.violations is None:
            self.violations = []
        if self.injuries_reported is None:
            self.injuries_reported = []
        if self.witness_statements is None:
            self.witness_statements = []
        if self.citations_issued is None:
            self.citations_issued = []
        if self.towed_vehicles is None:
            self.towed_vehicles = []

class LegalCaseProcessor(EmailPDFAgent):
    """Enhanced Legal Case Processing Agent"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Legal Case Processor"""
        super().__init__(config)
        
        # Create specialized agents for different tasks
        self.extraction_agent = self._create_extraction_agent()
        self.analysis_agent = self._create_analysis_agent()
        self.location_agent = self._create_location_agent()
        self.attorney_agent = self._create_attorney_agent()
        self.police_report_agent = self._create_police_report_agent()
        self.multi_report_analyzer = self._create_multi_report_analyzer()
        
        logger.info("Legal Case Processor initialized")
    
    def _create_model(self, max_tokens=4000, temperature=0.1):
        """Create model based on configuration"""
        provider = self.config.get('model_provider', 'openai').lower()
        model_name = self.config.get('model_name', 'gpt-4o')
        
        if provider == 'openai':
            return OpenAIChat(
                id=model_name,
                max_tokens=max_tokens,
                temperature=temperature
            )
        elif provider == 'anthropic':
            return Claude(
                id=model_name,
                max_tokens=max_tokens,
                temperature=temperature
            )
        elif provider == 'google':
            return Gemini(
                id=model_name,
                temperature=temperature
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")
    
    def _create_extraction_agent(self) -> Agent:
        """Create agent for case data extraction"""
        model = self._create_model(max_tokens=4000, temperature=0.1)
        
        agent = Agent(
            name="Legal Case Data Extraction Agent",
            model=model,
            instructions=[
                "You are an expert legal case data extraction specialist.",
                "Extract structured information from legal documents and emails.",
                "Focus on identifying key case elements: client info, accident details, injuries, treatment, insurance, liability.",
                "Be thorough but precise in your extractions.",
                "If information is unclear or missing, note this explicitly.",
                "Pay special attention to dates, names, medical terms, and financial information.",
                "Format your response as structured JSON when requested.",
            ],
            markdown=True,
        )
        
        return agent
    
    def _create_analysis_agent(self) -> Agent:
        """Create agent for underwriting analysis"""
        model = self._create_model(max_tokens=4000, temperature=0.1)
        
        agent = Agent(
            name="Legal Underwriting Analysis Agent",
            model=model,
            instructions=[
                "You are an expert legal underwriting analyst.",
                "Identify gaps in case information that are critical for underwriting decisions.",
                "Generate intelligent follow-up questions for law firms.",
                "Assess case strength, liability issues, and potential exposure.",
                "Consider medical treatment patterns, injury severity, and documentation quality.",
                "Flag red flags or inconsistencies in the case information.",
                "Provide actionable insights for underwriters.",
            ],
            markdown=True,
        )
        
        return agent
    
    def _create_location_agent(self) -> Agent:
        """Create agent for location risk analysis"""
        model = self._create_model(max_tokens=2000, temperature=0.1)
        
        agent = Agent(
            name="Location Risk Analysis Agent",
            model=model,
            instructions=[
                "You are an expert in geographic risk analysis for legal cases.",
                "Analyze accident locations for tort environment and jury tendencies.",
                "Consider political demographics, historical verdict patterns, and local legal culture.",
                "Classify jurisdictions as tort-friendly, neutral, or tort-hostile.",
                "Provide insights on potential settlement values and litigation risks.",
                "Base analysis on known data about counties, cities, and regions.",
            ],
            markdown=True,
        )
        
        return agent
    
    def _create_attorney_agent(self) -> Agent:
        """Create agent for attorney verification"""
        model = self._create_model(max_tokens=2000, temperature=0.1)
        
        agent = Agent(
            name="Attorney Verification Agent",
            model=model,
            instructions=[
                "You are an expert in attorney background verification.",
                "Analyze attorney information for credibility and legitimacy.",
                "Consider experience, specialization, and professional standing.",
                "Flag potential issues with unlicensed practice or questionable firms.",
                "Provide insights on attorney capability and case handling likelihood.",
            ],
            markdown=True,
        )
        
        return agent
    
    def _create_police_report_agent(self) -> Agent:
        """Create agent for police report data extraction"""
        model = self._create_model(max_tokens=4000, temperature=0.1)
        
        agent = Agent(
            name="Police Report Data Extraction Agent",
            model=model,
            instructions=[
                "You are an expert in extracting and analyzing police report data.",
                "Extract structured information from police reports.",
                "Focus on key details: report number, dates, parties involved, vehicles, violations, narrative.",
                "Identify any indications of fault or liability.",
                "Be thorough and accurate in data extractions.",
                "If information is unclear or missing, note this explicitly.",
                "Format your response as structured JSON when requested.",
            ],
            markdown=True,
        )
        
        return agent
    
    def _create_multi_report_analyzer(self) -> Agent:
        """Create agent for analyzing multiple reports and synthesizing information"""
        model = self._create_model(max_tokens=4000, temperature=0.1)
        
        agent = Agent(
            name="Multi-Report Analysis Agent",
            model=model,
            instructions=[
                "You are an expert in analyzing and synthesizing information from multiple reports.",
                "Compare and contrast data from different sources for consistency and discrepancies.",
                "Identify key patterns, trends, and anomalies across reports.",
                "Provide a synthesized summary with highlights and critical insights.",
                "Flag any conflicting information or major gaps in the data.",
                "Assist in forming a comprehensive understanding of the case from multiple data points.",
            ],
            markdown=True,
        )
        
        return agent
    
    def extract_case_data(self, text_content: str, email_body: str = "") -> CaseData:
        """Extract structured case data from PDF content and email"""
        try:
            logger.info("Extracting case data from documents")
            
            # Combine PDF content and email body
            full_content = f"""
            EMAIL BODY:
            {email_body}
            
            PDF CONTENT:
            {text_content}
            """
            
            extraction_prompt = f"""
            Please extract the following case information from the provided content and format as JSON:
            
            {{
                "client_name": "Name of the injured party/claimant",
                "date_of_loss": "Date when accident/incident occurred",
                "accident_type": "Type of accident (auto, slip/fall, etc.)",
                "injuries": ["List of specific injuries mentioned"],
                "treatment": ["List of medical treatments received"],
                "medical_providers": ["Names of doctors, hospitals, clinics"],
                "insurance_info": "Insurance company and coverage details",
                "policy_limits": "Policy limits if mentioned",
                "liability_info": "Liability/fault information",
                "attorney_name": "Name of the attorney/lawyer",
                "attorney_email": "Email address of attorney",
                "law_firm": "Name of law firm",
                "accident_location": "Location where accident occurred"
            }}
            
            Content to analyze:
            {full_content}
            
            Important: Only include information that is explicitly stated. Use null for missing information.
            """
            
            response = self.extraction_agent.run(extraction_prompt)
            
            # Parse JSON from response
            try:
                # Extract JSON from response text
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    data_dict = json.loads(json_match.group())
                    case_data = CaseData(**data_dict)
                else:
                    # Fallback: create case data from text analysis
                    case_data = self._parse_case_data_from_text(response.content)
                
                logger.info(f"Successfully extracted case data for client: {case_data.client_name}")
                return case_data
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON, using text-based extraction")
                return self._parse_case_data_from_text(response.content)
                
        except Exception as e:
            logger.error(f"Error extracting case data: {e}")
            return CaseData()
    
    def _parse_case_data_from_text(self, text: str) -> CaseData:
        """Fallback method to parse case data from text"""
        case_data = CaseData()
        
        # Simple regex patterns for common information
        patterns = {
            'client_name': r'(?:client|claimant|plaintiff):\s*([^\n]+)',
            'date_of_loss': r'(?:date of loss|accident date|incident date):\s*([^\n]+)',
            'accident_type': r'(?:accident type|incident type):\s*([^\n]+)',
            'attorney_name': r'(?:attorney|lawyer):\s*([^\n]+)',
            'attorney_email': r'(?:email|e-mail):\s*([^\s@]+@[^\s@]+\.[^\s@]+)',
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                setattr(case_data, field, match.group(1).strip())
        
        return case_data
    
    def identify_missing_information(self, case_data: CaseData) -> List[str]:
        """Identify gaps in case information and generate follow-up questions"""
        try:
            logger.info("Analyzing case for missing information")
            
            analysis_prompt = f"""
            Analyze the following case information and identify what critical information is missing 
            for proper underwriting analysis. Generate specific follow-up questions.
            
            Case Data:
            - Client Name: {case_data.client_name}
            - Date of Loss: {case_data.date_of_loss}
            - Accident Type: {case_data.accident_type}
            - Injuries: {', '.join(case_data.injuries) if case_data.injuries else 'Not specified'}
            - Treatment: {', '.join(case_data.treatment) if case_data.treatment else 'Not specified'}
            - Medical Providers: {', '.join(case_data.medical_providers) if case_data.medical_providers else 'Not specified'}
            - Insurance Info: {case_data.insurance_info}
            - Policy Limits: {case_data.policy_limits}
            - Liability Info: {case_data.liability_info}
            - Accident Location: {case_data.accident_location}
            
            Please provide:
            1. A bullet list of missing critical information
            2. Specific follow-up questions to ask the law firm
            3. Priority level for each missing item (High/Medium/Low)
            
            Focus on information essential for underwriting decisions.
            """
            
            response = self.analysis_agent.run(analysis_prompt)
            
            # Extract missing items from response
            missing_items = []
            lines = response.content.split('\n')
            for line in lines:
                if line.strip().startswith('•') or line.strip().startswith('-') or line.strip().startswith('*'):
                    missing_items.append(line.strip())
            
            logger.info(f"Identified {len(missing_items)} missing information items")
            return missing_items
            
        except Exception as e:
            logger.error(f"Error analyzing missing information: {e}")
            return ["Error analyzing case completeness"]
    
    def analyze_location_risk(self, location: str) -> LocationAnalysis:
        """Analyze location for tort environment and risk factors"""
        try:
            if not location:
                return LocationAnalysis()
                
            logger.info(f"Analyzing location risk for: {location}")
            
            location_prompt = f"""
            Analyze the legal/tort environment for the following location: {location}
            
            Please provide analysis on:
            1. Political demographics (liberal/conservative leaning)
            2. Historical jury verdict patterns
            3. Tort-friendly vs tort-hostile environment
            4. Settlement vs litigation tendencies
            5. Overall risk assessment for insurance claims
            6. Notable local legal factors
            
            Format your response with clear sections and risk level assessment.
            """
            
            response = self.location_agent.run(location_prompt)
            
            # Parse response into LocationAnalysis
            analysis = LocationAnalysis()
            content = response.content.lower()
            
            # Extract key information
            if 'liberal' in content or 'democrat' in content:
                analysis.political_leaning = 'Liberal'
            elif 'conservative' in content or 'republican' in content:
                analysis.political_leaning = 'Conservative'
            else:
                analysis.political_leaning = 'Mixed/Neutral'
            
            if 'tort-friendly' in content or 'plaintiff-friendly' in content:
                analysis.tort_environment = 'Tort-Friendly'
                analysis.risk_level = 'High'
            elif 'tort-hostile' in content or 'defense-friendly' in content:
                analysis.tort_environment = 'Tort-Hostile'
                analysis.risk_level = 'Low'
            else:
                analysis.tort_environment = 'Neutral'
                analysis.risk_level = 'Medium'
            
            # Parse location components
            location_parts = location.split(',')
            if len(location_parts) >= 2:
                analysis.city = location_parts[0].strip()
                analysis.state = location_parts[-1].strip()
                if len(location_parts) >= 3:
                    analysis.county = location_parts[1].strip()
            
            analysis.notes = response.content
            
            logger.info(f"Location analysis complete: {analysis.risk_level} risk")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing location risk: {e}")
            return LocationAnalysis(notes=f"Error analyzing location: {e}")
    
    def verify_attorney(self, attorney_name: str, attorney_email: str, state: str = None) -> AttorneyVerification:
        """Verify attorney credentials and legitimacy"""
        try:
            if not attorney_name:
                return AttorneyVerification()
                
            logger.info(f"Verifying attorney: {attorney_name}")
            
            verification_prompt = f"""
            Analyze the following attorney information for legitimacy and professional standing:
            
            Attorney Name: {attorney_name}
            Email: {attorney_email}
            State: {state or 'Unknown'}
            
            Please provide analysis on:
            1. Typical bar admission patterns for this name
            2. Email domain legitimacy (professional vs generic)
            3. Common red flags or legitimacy indicators
            4. Recommended verification steps
            5. Overall credibility assessment
            
            Note: This is for general analysis only, not actual bar database lookup.
            """
            
            response = self.attorney_agent.run(verification_prompt)
            
            verification = AttorneyVerification()
            verification.name = attorney_name
            verification.state = state
            verification.notes = response.content
            
            # Simple email verification
            if attorney_email:
                domain = attorney_email.split('@')[-1] if '@' in attorney_email else ''
                if domain and not domain.endswith(('.gmail.com', '.yahoo.com', '.hotmail.com')):
                    verification.email_verified = True
                    verification.firm_verified = True
            
            # Parse response for status indicators
            content = response.content.lower()
            if 'legitimate' in content or 'professional' in content:
                verification.bar_status = 'Likely Active'
            elif 'questionable' in content or 'red flag' in content:
                verification.bar_status = 'Requires Verification'
            else:
                verification.bar_status = 'Unknown'
            
            logger.info(f"Attorney verification complete: {verification.bar_status}")
            return verification
            
        except Exception as e:
            logger.error(f"Error verifying attorney: {e}")
            return AttorneyVerification(notes=f"Error verifying attorney: {e}")
    
    def extract_police_report_data(self, text_content: str) -> PoliceReportData:
        """Extract structured police report data from text content"""
        try:
            logger.info("Extracting police report data from text content")
            
            extraction_prompt = f"""
            Please extract the following police report information from the provided text and format as JSON:
            
            {{
                "report_number": "Report number of the police report",
                "report_date": "Date when the report was filed",
                "incident_date": "Date when the incident occurred",
                "incident_time": "Time when the incident occurred",
                "location": "Location of the incident",
                "officers": ["List of officers mentioned in the report"],
                "parties_involved": ["List of parties involved in the incident"],
                "vehicles": ["List of vehicles involved"],
                "violations": ["List of violations or charges"],
                "narrative": "Narrative description of the incident",
                "weather_conditions": "Weather conditions at the time of the incident",
                "road_conditions": "Road conditions at the time of the incident",
                "traffic_control": "Traffic control measures in place",
                "damage_assessment": "Assessment of damages",
                "injuries_reported": ["List of reported injuries"],
                "fault_determination": "Determination of fault or liability",
                "witness_statements": ["List of witness statements"],
                "citations_issued": ["List of citations issued"],
                "towed_vehicles": ["List of towed vehicles"],
                "property_damage": "Description of property damage"
            }}
            
            Text to analyze:
            {text_content}
            
            Important: Only include information that is explicitly stated. Use null for missing information.
            """
            
            response = self.extraction_agent.run(extraction_prompt)
            
            # Parse JSON from response
            try:
                # Extract JSON from response text
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    data_dict = json.loads(json_match.group())
                    police_report_data = PoliceReportData(**data_dict)
                else:
                    logger.warning("No JSON object found in response")
                    police_report_data = PoliceReportData()
                
                logger.info("Successfully extracted police report data")
                return police_report_data
                
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from police report data extraction")
                return PoliceReportData()
                
        except Exception as e:
            logger.error(f"Error extracting police report data: {e}")
            return PoliceReportData()
    
    def process_multiple_police_reports(self, text_contents: List[str]) -> List[PoliceReportData]:
        """Process multiple police reports and extract data from each"""
        try:
            logger.info(f"Processing {len(text_contents)} police reports")
            
            reports = []
            for i, text_content in enumerate(text_contents):
                logger.info(f"Processing police report {i+1} of {len(text_contents)}")
                report_data = self.extract_police_report_data(text_content)
                reports.append(report_data)
            
            logger.info(f"Successfully processed {len(reports)} police reports")
            return reports
            
        except Exception as e:
            logger.error(f"Error processing multiple police reports: {e}")
            return []
    
    def analyze_multiple_reports(self, case_data: CaseData, police_reports: List[PoliceReportData]) -> Dict[str, Any]:
        """Analyze multiple police reports and provide consolidated insights"""
        try:
            logger.info(f"Analyzing {len(police_reports)} police reports for consistency and insights")
            
            # Create summary of all reports
            reports_summary = []
            for i, report in enumerate(police_reports):
                summary = {
                    "report_number": report.report_number,
                    "incident_date": report.incident_date,
                    "location": report.location,
                    "parties_involved": report.parties_involved,
                    "fault_determination": report.fault_determination,
                    "violations": report.violations,
                    "injuries_reported": report.injuries_reported,
                    "narrative_snippet": report.narrative[:200] + "..." if report.narrative and len(report.narrative) > 200 else report.narrative
                }
                reports_summary.append(summary)
            
            analysis_prompt = f"""
            Analyze the following multiple police reports for a legal case and provide comprehensive insights:
            
            Case Information:
            - Client: {case_data.client_name}
            - Accident Type: {case_data.accident_type}
            - Date of Loss: {case_data.date_of_loss}
            
            Police Reports Summary:
            {json.dumps(reports_summary, indent=2)}
            
            Please provide a detailed analysis covering:
            
            1. **Consistency Analysis**: Are the reports consistent with each other? Any discrepancies in facts, dates, locations, or fault determinations?
            
            2. **Fault and Liability**: What do the reports indicate about fault and liability? Are there clear patterns or conflicting assessments?
            
            3. **Injury Correlation**: How do reported injuries in police reports align with the case medical information?
            
            4. **Key Evidence**: What are the most important pieces of evidence from these reports?
            
            5. **Red Flags**: Any concerning inconsistencies, missing information, or suspicious patterns?
            
            6. **Overall Assessment**: How do these reports strengthen or weaken the case?
            
            7. **Recommendations**: What additional information or clarification should be requested?
            
            Format your response with clear headings and bullet points for easy reading.
            """
            
            response = self.multi_report_analyzer.run(analysis_prompt)
            
            # Create structured analysis result
            analysis_result = {
                "number_of_reports": len(police_reports),
                "reports_analyzed": [r.report_number for r in police_reports if r.report_number],
                "analysis": response.content,
                "key_findings": self._extract_key_findings(response.content),
                "consistency_score": self._assess_consistency(police_reports),
                "recommendations": self._extract_recommendations(response.content)
            }
            
            logger.info("Multi-report analysis completed")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing multiple reports: {e}")
            return {
                "number_of_reports": len(police_reports),
                "error": str(e),
                "analysis": "Error occurred during analysis"
            }
    
    def _extract_key_findings(self, analysis_text: str) -> List[str]:
        """Extract key findings from analysis text"""
        findings = []
        lines = analysis_text.split('\n')
        
        in_key_section = False
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['key evidence', 'important', 'critical', 'red flag']):
                in_key_section = True
            elif line.startswith('##') or line.startswith('#'):
                in_key_section = False
            elif in_key_section and line.startswith('-'):
                findings.append(line[1:].strip())
        
        return findings[:5]  # Return top 5 findings
    
    def _assess_consistency(self, police_reports: List[PoliceReportData]) -> str:
        """Assess consistency across multiple police reports"""
        if len(police_reports) < 2:
            return "Single report - consistency assessment not applicable"
        
        # Check consistency of key fields
        incident_dates = set(r.incident_date for r in police_reports if r.incident_date)
        locations = set(r.location for r in police_reports if r.location)
        fault_determinations = set(r.fault_determination for r in police_reports if r.fault_determination)
        
        inconsistencies = []
        if len(incident_dates) > 1:
            inconsistencies.append("incident dates")
        if len(locations) > 1:
            inconsistencies.append("locations")
        if len(fault_determinations) > 1:
            inconsistencies.append("fault determinations")
        
        if not inconsistencies:
            return "High - All key fields are consistent"
        elif len(inconsistencies) <= 2:
            return f"Medium - Some inconsistencies in: {', '.join(inconsistencies)}"
        else:
            return f"Low - Multiple inconsistencies in: {', '.join(inconsistencies)}"
    
    def _extract_recommendations(self, analysis_text: str) -> List[str]:
        """Extract recommendations from analysis text"""
        recommendations = []
        lines = analysis_text.split('\n')
        
        in_rec_section = False
        for line in lines:
            line = line.strip()
            if 'recommendation' in line.lower():
                in_rec_section = True
            elif line.startswith('##') or line.startswith('#'):
                in_rec_section = False
            elif in_rec_section and line.startswith('-'):
                recommendations.append(line[1:].strip())
        
        return recommendations[:3]  # Return top 3 recommendations

    def _identify_separate_reports(self, content: str) -> List[str]:
        """Identify and separate multiple police reports in content"""
        # Look for report separators
        separators = [
            'POLICE REPORT',
            'INCIDENT REPORT', 
            'ACCIDENT REPORT',
            'REPORT NUMBER',
            'REPORT #'
        ]
        
        reports = []
        lines = content.split('\n')
        current_report = []
        
        for line in lines:
            line_upper = line.upper()
            if any(sep in line_upper for sep in separators) and current_report:
                # Found a new report, save the current one
                reports.append('\n'.join(current_report))
                current_report = [line]
            else:
                current_report.append(line)
        
        # Add the last report
        if current_report:
            reports.append('\n'.join(current_report))
        
        # Filter out very short "reports" (likely false positives)
        reports = [report for report in reports if len(report.split()) > 50]
        
        return reports if len(reports) > 1 else [content]

    def generate_comprehensive_report(self, case_data: CaseData, missing_info: List[str], 
                                    location_analysis: LocationAnalysis, 
                                    attorney_verification: AttorneyVerification,
                                    original_sender: str, original_subject: str,
                                    police_report_data: PoliceReportData = None,
                                    multi_report_analysis: Dict[str, Any] = None) -> str:
        """Generate comprehensive case analysis report"""
        try:
            logger.info("Generating comprehensive case report")
            
            report = f"""
# Case Summary: {case_data.client_name or 'Unknown Client'} | {case_data.accident_type or 'Unknown Incident'} | {location_analysis.city or 'Unknown Location'}

Hi Ron,

Here's a comprehensive analysis of the forwarded case email:

## 📄 Case Summary (Extracted from Attachments)

**Claimant:** {case_data.client_name or 'Not specified'}
**Date of Loss:** {case_data.date_of_loss or 'Not specified'}
**Accident Type:** {case_data.accident_type or 'Not specified'}
**Location:** {case_data.accident_location or 'Not specified'}

### Injuries & Treatment
{self._format_list_section(case_data.injuries, 'No injuries specified')}

### Medical Treatment
{self._format_list_section(case_data.treatment, 'No treatment information specified')}

### Medical Providers
{self._format_list_section(case_data.medical_providers, 'No medical providers specified')}

### Insurance Information
**Insurance Company:** {case_data.insurance_info or 'Not specified'}
**Policy Limits:** {case_data.policy_limits or 'Not disclosed'}

### Liability Information
{case_data.liability_info or 'Not specified'}

## ❗ Missing Info / Follow-Ups Needed

{self._format_missing_info(missing_info)}

## 🌍 Location Risk Analysis

**Accident Location:** {location_analysis.city or 'Unknown'}, {location_analysis.state or 'Unknown'}
**Political Leaning:** {location_analysis.political_leaning or 'Unknown'}
**Tort Environment:** {location_analysis.tort_environment or 'Unknown'}
**Risk Level:** {location_analysis.risk_level or 'Unknown'}

**Analysis Notes:**
{location_analysis.notes or 'No detailed analysis available'}

## ⚖️ Attorney License Verification

**Name:** {attorney_verification.name or 'Not specified'}
**Estimated Bar Status:** {attorney_verification.bar_status or 'Unknown'}
**Email Domain:** {'Professional' if attorney_verification.email_verified else 'Generic/Unknown'}
**Firm Verification:** {'✅ Professional Domain' if attorney_verification.firm_verified else '⚠️  Generic Email Domain'}

**Verification Notes:**
{attorney_verification.notes or 'No verification performed'}

## 🚔 Police Report Data

**Report Number:** {police_report_data.report_number or 'Not specified'}
**Report Date:** {police_report_data.report_date or 'Not specified'}
**Incident Date:** {police_report_data.incident_date or 'Not specified'}
**Incident Time:** {police_report_data.incident_time or 'Not specified'}
**Location:** {police_report_data.location or 'Not specified'}

### Officers Involved
{self._format_list_section(police_report_data.officers, 'No officers specified')}

### Parties Involved
{self._format_list_section(police_report_data.parties_involved, 'No parties specified')}

### Vehicles Involved
{self._format_list_section(police_report_data.vehicles, 'No vehicles specified')}

### Violations
{self._format_list_section(police_report_data.violations, 'No violations specified')}

### Injuries Reported
{self._format_list_section(police_report_data.injuries_reported, 'No injuries reported')}

### Witness Statements
{self._format_list_section(police_report_data.witness_statements, 'No witness statements')}

**Narrative:**
{police_report_data.narrative or 'No narrative provided'}

**Weather Conditions:** {police_report_data.weather_conditions or 'Not specified'}
**Road Conditions:** {police_report_data.road_conditions or 'Not specified'}
**Traffic Control:** {police_report_data.traffic_control or 'Not specified'}
**Damage Assessment:** {police_report_data.damage_assessment or 'Not specified'}
**Fault Determination:** {police_report_data.fault_determination or 'Not specified'}

---

## 📑 Multi-Report Analysis (if applicable)

{multi_report_analysis['analysis'] if multi_report_analysis else 'No multi-report analysis performed'}

**Key Findings:**
- {multi_report_analysis['key_findings'][0] if multi_report_analysis and 'key_findings' in multi_report_analysis and len(multi_report_analysis['key_findings']) > 0 else 'No key findings'}
- {multi_report_analysis['key_findings'][1] if multi_report_analysis and 'key_findings' in multi_report_analysis and len(multi_report_analysis['key_findings']) > 1 else ''}
- {multi_report_analysis['key_findings'][2] if multi_report_analysis and 'key_findings' in multi_report_analysis and len(multi_report_analysis['key_findings']) > 2 else ''}

**Consistency Score:** {multi_report_analysis['consistency_score'] if multi_report_analysis else 'N/A'}

**Recommendations:**
- {multi_report_analysis['recommendations'][0] if multi_report_analysis and 'recommendations' in multi_report_analysis and len(multi_report_analysis['recommendations']) > 0 else 'No recommendations'}
- {multi_report_analysis['recommendations'][1] if multi_report_analysis and 'recommendations' in multi_report_analysis and len(multi_report_analysis['recommendations']) > 1 else ''}
- {multi_report_analysis['recommendations'][2] if multi_report_analysis and 'recommendations' in multi_report_analysis and len(multi_report_analysis['recommendations']) > 2 else ''}

*For detailed multi-report analysis, refer to the attached document.*

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Original Email: {original_subject} from {original_sender}*
            """
            
            logger.info("Comprehensive report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return f"Error generating report: {e}"
    
    def _format_list_section(self, items: List[str], default_text: str) -> str:
        """Format a list section for the report"""
        if not items:
            return default_text
        return '\n'.join([f"• {item}" for item in items])
    
    def _format_missing_info(self, missing_info: List[str]) -> str:
        """Format missing information section"""
        if not missing_info:
            return "• All essential information appears to be present"
        return '\n'.join(missing_info)
    
    def process_legal_case_email(self, email_body: str, pdf_attachments: List[str], 
                               sender_email: str, subject: str) -> str:
        """Main method to process a legal case email through the full pipeline"""
        try:
            logger.info(f"Processing legal case email from {sender_email}")
            
            # Step 1: Extract text from all PDF attachments
            all_pdf_text = ""
            for pdf_path in pdf_attachments:
                try:
                    pdf_text = self.extract_text_from_pdf(pdf_path)
                    all_pdf_text += f"\n\n--- {os.path.basename(pdf_path)} ---\n{pdf_text}"
                except Exception as e:
                    logger.error(f"Error processing PDF {pdf_path}: {e}")
                    all_pdf_text += f"\n\n--- {os.path.basename(pdf_path)} ---\nError extracting text: {e}"
            
            # Step 2: Extract case data
            case_data = self.extract_case_data(all_pdf_text, email_body)
            
            # Step 3: Identify missing information
            missing_info = self.identify_missing_information(case_data)
            
            # Step 4: Analyze location risk
            location_analysis = self.analyze_location_risk(case_data.accident_location)
            
            # Step 5: Verify attorney
            attorney_verification = self.verify_attorney(
                case_data.attorney_name, 
                case_data.attorney_email or sender_email,
                location_analysis.state
            )
            
            # Step 6: Extract police report data (with multi-report support)
            police_report_data = None
            multi_report_analysis = None
            
            # Check if we have potential police reports
            if any(keyword in (subject.lower() + " " + email_body.lower() + " " + all_pdf_text.lower()) 
                   for keyword in ['police report', 'incident report', 'accident report']):
                
                # Identify separate reports
                potential_reports = self._identify_separate_reports(all_pdf_text)
                
                if len(potential_reports) > 1:
                    logger.info(f"Found {len(potential_reports)} potential police reports")
                    police_reports = self.process_multiple_police_reports(potential_reports)
                    multi_report_analysis = self.analyze_multiple_reports(case_data, police_reports)
                    # Use the first report for the main police report data
                    police_report_data = police_reports[0] if police_reports else None
                else:
                    # Single report processing
                    police_report_data = self.extract_police_report_data(all_pdf_text)
            
            # Step 7: Generate comprehensive report
            report = self.generate_comprehensive_report(
                case_data, missing_info, location_analysis, 
                attorney_verification, sender_email, subject,
                police_report_data, multi_report_analysis
            )
            
            logger.info("Legal case processing completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error processing legal case email: {e}")
            return f"Error processing legal case: {e}"

def main():
    """Main function for testing the Legal Case Processor with multi-report functionality"""
    # Test with sample data
    processor = LegalCaseProcessor()
    
    # Sample email data
    sample_email_body = """
    Dear Ron,
    
    Please find attached the medical records and multiple police reports for our client Jane Doe's 
    auto accident case. The accident occurred on May 3, 2024, in Los Angeles, CA.
    
    Client was rear-ended and suffered neck and back injuries. She has been treated
    by Dr. Smith at LA Orthopedics.
    
    We have both the initial police report and the follow-up investigation report.
    
    Best regards,
    Sarah Levine, Esq.
    Levine & Associates
    """
    
    # This would normally process actual PDF files - simulating multiple reports
    sample_pdf_content = """
    POLICE REPORT
    Report Number: PR-2024-001234
    Date of Accident: May 3, 2024
    Location: Sunset Blvd, Los Angeles, CA
    Vehicles Involved: 2019 Honda Civic, 2020 Ford F-150
    
    Driver 1: Jane Doe (not at fault)
    Driver 2: John Smith (at fault - following too closely)
    
    Narrative: Vehicle 2 was following too closely behind Vehicle 1 when traffic came to a sudden stop. 
    Vehicle 2 rear-ended Vehicle 1 causing moderate damage to both vehicles.
    
    Citations Issued: Following too closely - John Smith
    
    POLICE REPORT
    Report Number: PR-2024-001235
    Date: May 5, 2024 (Follow-up Investigation)
    Location: Sunset Blvd, Los Angeles, CA
    
    Follow-up investigation confirms initial findings. Vehicle 2 driver admits to distracted driving.
    Additional witness statements collected.
    
    Fault Determination: John Smith - 100% at fault
    
    MEDICAL RECORDS
    Patient: Jane Doe
    DOB: 01/15/1985
    
    Injuries: Cervical strain, lumbar strain, minor concussion
    Treatment: Physical therapy, MRI ordered, neurological evaluation
    Provider: Dr. Michael Smith, LA Orthopedics
    """
    
    # Process the case with multiple reports
    case_data = processor.extract_case_data(sample_pdf_content, sample_email_body)
    missing_info = processor.identify_missing_information(case_data)
    location_analysis = processor.analyze_location_risk("Los Angeles, CA")
    attorney_verification = processor.verify_attorney("Sarah Levine", "sarah@levinelaw.com", "CA")
    
    # Test multi-report functionality
    potential_reports = processor._identify_separate_reports(sample_pdf_content)
    print(f"Found {len(potential_reports)} potential reports")
    
    if len(potential_reports) > 1:
        police_reports = processor.process_multiple_police_reports(potential_reports)
        multi_report_analysis = processor.analyze_multiple_reports(case_data, police_reports)
        police_report_data = police_reports[0] if police_reports else None
        
        report = processor.generate_comprehensive_report(
            case_data, missing_info, location_analysis, 
            attorney_verification, "sarah@levinelaw.com", "Auto Accident Case - Multiple Police Reports - Jane Doe",
            police_report_data, multi_report_analysis
        )
    else:
        police_report_data = processor.extract_police_report_data(sample_pdf_content)
        report = processor.generate_comprehensive_report(
            case_data, missing_info, location_analysis, 
            attorney_verification, "sarah@levinelaw.com", "Auto Accident Case - Jane Doe",
            police_report_data
        )
    
    print("="*80)
    print("COMPREHENSIVE LEGAL CASE REPORT WITH MULTI-REPORT ANALYSIS")
    print("="*80)
    print(report)

if __name__ == "__main__":
    main()
