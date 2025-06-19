#!/usr/bin/env python3
"""
Test script for multi-police report functionality
Tests the ability to process multiple police reports and provide consolidated analysis
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from legal_case_processor import LegalCaseProcessor

def test_multi_police_reports():
    """Test processing multiple police reports"""
    print("Testing Multi-Police Report Analysis")
    print("="*50)
    
    # Initialize processor
    processor = LegalCaseProcessor()
    
    # Sample content with multiple police reports
    multi_report_content = """
    POLICE REPORT
    Report Number: 2024-LA-001234
    Report Date: May 3, 2024
    Incident Date: May 3, 2024
    Incident Time: 3:45 PM
    Location: Intersection of Sunset Blvd and Vine St, Los Angeles, CA
    
    Officers: Officer Johnson #4521, Officer Martinez #3892
    
    Parties Involved:
    - Jane Doe (Driver, Vehicle 1)
    - John Smith (Driver, Vehicle 2)
    
    Vehicles:
    - 2019 Honda Civic (Jane Doe)
    - 2020 Ford F-150 (John Smith)
    
    Narrative: At approximately 3:45 PM, Vehicle 2 (Ford F-150) was traveling northbound on Vine St 
    when it failed to stop at the red light and collided with Vehicle 1 (Honda Civic) which was 
    traveling eastbound on Sunset Blvd with a green light.
    
    Violations: Running red light - John Smith
    Citations Issued: Traffic violation - John Smith
    Fault Determination: John Smith - 100% at fault
    Weather Conditions: Clear
    Road Conditions: Dry
    
    Injuries Reported: Jane Doe - complained of neck and back pain
    
    POLICE REPORT
    Report Number: 2024-LA-001235
    Report Date: May 5, 2024 (Follow-up Investigation)
    Incident Date: May 3, 2024
    Location: Intersection of Sunset Blvd and Vine St, Los Angeles, CA
    
    Officers: Officer Wilson #2847, Sergeant Davis #1523
    
    Follow-up Investigation Report:
    Additional witness interviews conducted. Traffic camera footage reviewed.
    
    Witness Statements:
    - Maria Garcia: "I saw the red truck run the red light"
    - Robert Chen: "The Honda had the right of way, definitely"
    
    Updated Fault Determination: John Smith - 100% at fault (confirmed)
    Additional Notes: Driver Smith admits to being distracted by phone at time of accident
    
    POLICE REPORT
    Report Number: 2024-LA-001236
    Report Date: May 10, 2024 (Accident Reconstruction)
    Incident Date: May 3, 2024
    Location: Intersection of Sunset Blvd and Vine St, Los Angeles, CA
    
    Officers: Accident Reconstructionist Thompson #9876
    
    Accident Reconstruction Report:
    Speed analysis indicates Vehicle 2 was traveling approximately 35 mph in a 25 mph zone.
    Impact analysis confirms Vehicle 2 struck Vehicle 1 in the passenger side.
    
    Physical Evidence:
    - Skid marks: 45 feet from Vehicle 2
    - Impact damage consistent with T-bone collision
    - No evidence of evasive action by Vehicle 1
    
    Final Determination: Vehicle 2 driver 100% at fault for running red light and speeding
    """
    
    # Test the multi-report identification
    print("1. Testing report identification...")
    potential_reports = processor._identify_separate_reports(multi_report_content)
    print(f"   Found {len(potential_reports)} separate reports")
    
    if len(potential_reports) > 1:
        print("\n2. Processing multiple reports...")
        police_reports = processor.process_multiple_police_reports(potential_reports)
        print(f"   Successfully processed {len(police_reports)} reports")
        
        # Display summary of each report
        for i, report in enumerate(police_reports):
            print(f"\n   Report {i+1} Summary:")
            print(f"     - Report Number: {report.report_number}")
            print(f"     - Report Date: {report.report_date}")
            print(f"     - Fault Determination: {report.fault_determination}")
            print(f"     - Officers: {', '.join(report.officers) if report.officers else 'None'}")
        
        print("\n3. Performing multi-report analysis...")
        
        # Create dummy case data for analysis
        from legal_case_processor import CaseData
        case_data = CaseData(
            client_name="Jane Doe",
            date_of_loss="May 3, 2024",
            accident_type="T-bone collision",
            accident_location="Intersection of Sunset Blvd and Vine St, Los Angeles, CA"
        )
        
        multi_report_analysis = processor.analyze_multiple_reports(case_data, police_reports)
        
        print(f"   Analysis completed for {multi_report_analysis['number_of_reports']} reports")
        print(f"   Consistency Score: {multi_report_analysis['consistency_score']}")
        print("\n   Key Findings:")
        for finding in multi_report_analysis['key_findings']:
            if finding:
                print(f"     • {finding}")
        
        print("\n   Recommendations:")
        for recommendation in multi_report_analysis['recommendations']:
            if recommendation:
                print(f"     • {recommendation}")
        
        print("\n4. Full Analysis Report:")
        print("-" * 80)
        print(multi_report_analysis['analysis'])
        print("-" * 80)
        
    else:
        print("   Only one report identified - multi-report analysis not applicable")
    
    print("\nTest completed successfully!")

def test_single_vs_multi_report():
    """Test the difference between single and multi-report processing"""
    print("\n" + "="*60)
    print("COMPARISON: Single vs Multi-Report Processing")
    print("="*60)
    
    processor = LegalCaseProcessor()
    
    # Single report content
    single_report = """
    POLICE REPORT
    Report Number: 2024-001
    Date: May 3, 2024
    Location: Main Street, LA
    Driver 1: Jane Doe - Not at fault
    Driver 2: John Smith - At fault (speeding)
    """
    
    # Multi-report content (simplified)
    multi_report = """
    POLICE REPORT
    Report Number: 2024-001
    Date: May 3, 2024
    Location: Main Street, LA
    Driver 1: Jane Doe - Not at fault
    Driver 2: John Smith - At fault (speeding)
    
    POLICE REPORT
    Report Number: 2024-002
    Date: May 5, 2024 (Follow-up)
    Location: Main Street, LA
    Updated findings: John Smith was also texting while driving
    Fault: John Smith - 100% at fault (confirmed)
    """
    
    print("\nSingle Report Processing:")
    single_reports = processor._identify_separate_reports(single_report)
    print(f"Reports identified: {len(single_reports)}")
    
    print("\nMulti-Report Processing:")
    multi_reports = processor._identify_separate_reports(multi_report)
    print(f"Reports identified: {len(multi_reports)}")
    
    if len(multi_reports) > 1:
        print("Multi-report analysis would be performed!")
    
if __name__ == "__main__":
    test_multi_police_reports()
    test_single_vs_multi_report()
