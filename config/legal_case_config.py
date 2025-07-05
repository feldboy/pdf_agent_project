#!/usr/bin/env python3
"""
Legal Case Processing Configuration

Configuration settings for the Legal Case Processing System
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LegalCaseConfig:
    """Configuration for Legal Case Processing System"""
    
    @staticmethod
    def get_config_dict():
        """Get configuration dictionary for legal case processing"""
        return {
            # Email monitoring settings
            'imap_server': os.getenv('IMAP_SERVER', 'imap.gmail.com'),
            'imap_port': int(os.getenv('IMAP_PORT', '993')),
            'email_address': os.getenv('EMAIL_ADDRESS'),
            'email_password': os.getenv('EMAIL_PASSWORD'),
            'monitor_folder': os.getenv('MONITOR_FOLDER', 'INBOX'),
            
            # Email sending settings
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL'),
            'sender_password': os.getenv('SENDER_PASSWORD'),
            'recipient_email': os.getenv('RECIPIENT_EMAIL'),  # Ron's email
            
            # Processing settings
            'check_interval': int(os.getenv('CHECK_INTERVAL', '300')),  # 5 minutes for legal cases
            'max_pdf_size': int(os.getenv('MAX_PDF_SIZE', '20971520')),  # 20MB for legal documents
            'process_all_pdfs': True,  # Always process all PDFs for legal cases
            
            # LLM settings
            'model_provider': os.getenv('MODEL_PROVIDER', 'openai'),
            'model_name': os.getenv('MODEL_NAME', 'gpt-4o'),  # Use GPT-4 for better analysis
            'max_tokens': int(os.getenv('MAX_TOKENS', '8000')),
            'temperature': float(os.getenv('TEMPERATURE', '0.1')),
            
            # Legal case specific settings
            'legal_keywords': [
                'case', 'claim', 'accident', 'injury', 'medical records',
                'police report', 'demand letter', 'settlement', 'litigation',
                'plaintiff', 'defendant', 'attorney', 'lawyer', 'law firm',
                'insurance', 'liability', 'damages', 'auto accident',
                'slip and fall', 'personal injury', 'workers comp',
                'premises liability', 'product liability', 'medical malpractice',
                'wrongful death', 'pain and suffering', 'loss of consortium'
            ],
            
            # Risk analysis settings
            'high_risk_keywords': [
                'wrongful death', 'catastrophic injury', 'permanent disability',
                'traumatic brain injury', 'spinal cord injury', 'amputation',
                'severe burns', 'multiple surgeries', 'ongoing treatment'
            ],
            
            # Location risk databases (simplified)
            'tort_friendly_locations': [
                'Los Angeles', 'San Francisco', 'New York', 'Chicago',
                'Philadelphia', 'Miami', 'Atlanta', 'Boston', 'Seattle'
            ],
            
            'tort_hostile_locations': [
                'Salt Lake City', 'Wichita', 'Oklahoma City', 'Tucson',
                'Virginia Beach', 'Colorado Springs', 'Mesa', 'Omaha'
            ],
            
            # Attorney verification settings
            'law_firm_domains': [
                '.law', 'legal', 'attorney', 'lawyer', 'esq', 'lawfirm',
                'counselor', 'advocate', 'barrister', 'solicitor'
            ],
            
            'generic_domains': [
                'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
                'aol.com', 'icloud.com', 'me.com', 'mac.com'
            ],
            
            # Report settings
            'include_location_analysis': True,
            'include_attorney_verification': True,
            'include_risk_assessment': True,
            'include_follow_up_questions': True,
            'include_case_timeline': True,
            
            # Notification settings
            'send_immediate_alerts': True,
            'alert_high_value_cases': True,
            'high_value_threshold': 50000,  # Cases potentially worth $50k+
            
            # Data retention settings
            'retain_processed_emails': True,
            'retain_extracted_data': True,
            'retention_days': 365,
            
            # Security settings
            'encrypt_sensitive_data': True,
            'log_all_activity': True,
            'require_sender_verification': False,  # Set to True for production
        }
    
    @staticmethod
    def validate_config():
        """Validate configuration and return list of missing items"""
        config = LegalCaseConfig.get_config_dict()
        missing = []
        
        # Required email settings
        required_fields = [
            'email_address', 'email_password', 'sender_email', 
            'sender_password', 'recipient_email'
        ]
        
        for field in required_fields:
            if not config.get(field):
                missing.append(f"Email setting: {field}")
        
        # Required API keys
        if config['model_provider'] == 'openai' and not os.getenv('OPENAI_API_KEY'):
            missing.append("OPENAI_API_KEY")
        elif config['model_provider'] == 'anthropic' and not os.getenv('ANTHROPIC_API_KEY'):
            missing.append("ANTHROPIC_API_KEY")
        elif config['model_provider'] == 'google' and not os.getenv('GOOGLE_API_KEY'):
            missing.append("GOOGLE_API_KEY")
        
        return missing
    
    @staticmethod
    def get_legal_case_instructions():
        """Get specialized instructions for legal case processing"""
        return [
            "You are a legal case analysis expert specializing in personal injury claims.",
            "Extract comprehensive case information including client details, incident facts, injuries, treatment, and liability.",
            "Focus on identifying key underwriting factors: policy limits, coverage issues, comparative negligence, damages exposure.",
            "Analyze case strength, documentation quality, and potential red flags.",
            "Consider jurisdiction-specific factors that may impact settlement values and litigation risk.",
            "Provide actionable insights for insurance adjusters and underwriters.",
            "Flag cases requiring immediate attention or specialized handling.",
            "Maintain professional tone and objective analysis throughout your assessment.",
            "Structure your analysis in a clear, logical format with appropriate headings and bullet points.",
            "Include specific recommendations for information gathering and case development."
        ]
    
    @staticmethod
    def get_extraction_prompts():
        """Get specialized prompts for data extraction"""
        return {
            'case_summary': """
            Extract the following case information and format as structured data:
            
            CLIENT INFORMATION:
            - Full name, DOB, contact information
            - Employment status, marital status, dependents
            
            INCIDENT DETAILS:
            - Date, time, and location of incident
            - Description of how incident occurred
            - Weather conditions, lighting, other environmental factors
            
            INJURIES & TREATMENT:
            - Specific injuries identified
            - Medical providers and facilities
            - Treatment received and recommended
            - Diagnostic tests and results
            - Surgical procedures performed or recommended
            
            LIABILITY ANALYSIS:
            - Parties involved and their roles
            - Potential fault/negligence factors
            - Witness information
            - Evidence available (photos, reports, etc.)
            
            INSURANCE INFORMATION:
            - Carriers for all parties
            - Policy limits and coverage types
            - Claims numbers and adjuster contacts
            
            LEGAL REPRESENTATION:
            - Attorney/law firm information
            - Experience and specialization
            - Anticipated legal strategy
            """,
            
            'medical_analysis': """
            Analyze the medical information provided and extract:
            
            INJURY SEVERITY:
            - Objective medical findings
            - Subjective complaints
            - Functional limitations
            - Prognosis for recovery
            
            TREATMENT APPROPRIATENESS:
            - Necessity of treatment received
            - Reasonableness of costs
            - Conservative vs. aggressive treatment approach
            - Compliance with treatment recommendations
            
            CAUSATION ANALYSIS:
            - Direct relationship between incident and injuries
            - Pre-existing conditions or degenerative changes
            - Intervening causes or subsequent injuries
            - Medical opinions on causation
            """,
            
            'damages_assessment': """
            Evaluate potential damages including:
            
            ECONOMIC DAMAGES:
            - Past and future medical expenses
            - Lost wages and earning capacity
            - Property damage
            - Out-of-pocket expenses
            
            NON-ECONOMIC DAMAGES:
            - Pain and suffering
            - Disability and disfigurement
            - Loss of enjoyment of life
            - Emotional distress
            
            SPECIAL DAMAGES:
            - Punitive damages potential
            - Loss of consortium claims
            - Wrongful death damages (if applicable)
            """
        }

# Example environment file template
ENV_TEMPLATE = """
# Legal Case Processing System Configuration
# Copy this to .env and fill in your actual values

# Email Settings (Gmail example)
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=ron@yourcompany.com

# IMAP/SMTP Settings (Gmail)
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Monitor Settings
MONITOR_FOLDER=INBOX
CHECK_INTERVAL=300

# LLM Settings
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o
MAX_TOKENS=8000
TEMPERATURE=0.1

# API Keys
OPENAI_API_KEY=your-openai-api-key
# ANTHROPIC_API_KEY=your-anthropic-api-key
# GOOGLE_API_KEY=your-google-api-key

# Processing Settings
MAX_PDF_SIZE=20971520
"""

def create_env_template():
    """Create a template .env file"""
    env_path = Path(__file__).parent / '.env.template'
    
    with open(env_path, 'w') as f:
        f.write(ENV_TEMPLATE)
    
    print(f"Environment template created at: {env_path}")
    print("Copy this to .env and fill in your actual values")

if __name__ == "__main__":
    # Create environment template
    create_env_template()
    
    # Validate current configuration
    config = LegalCaseConfig()
    missing = config.validate_config()
    
    if missing:
        print("Missing configuration items:")
        for item in missing:
            print(f"  - {item}")
    else:
        print("Configuration is complete!")
