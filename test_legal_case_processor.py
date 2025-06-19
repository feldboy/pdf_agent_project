#!/usr/bin/env python3
"""
Test script for Legal Case Processing System

This script tests the enhanced legal case processing capabilities including:
- Case data extraction
- Underwriting analysis  
- Location risk assessment
- Attorney verification
- Comprehensive report generation
"""

import os
import sys
import tempfile
import logging
from pathlib import Path
from legal_case_processor import LegalCaseProcessor, CaseData
from legal_case_monitor import LegalCaseMonitor

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_case_data_extraction():
    """Test case data extraction functionality"""
    print("🔍 Testing Case Data Extraction...")
    
    try:
        processor = LegalCaseProcessor()
        
        # Sample legal case content
        sample_pdf_content = """
        POLICE ACCIDENT REPORT
        Report Number: 2024-LA-001234
        Date of Accident: May 3, 2024
        Time: 2:30 PM
        Location: Sunset Blvd & Vine St, Los Angeles, CA 90028
        
        Vehicle 1: 2019 Honda Civic (Jane Doe - DOB: 01/15/1985)
        Vehicle 2: 2020 Ford F-150 (John Smith)
        
        Cause: Vehicle 2 following too closely, rear-ended Vehicle 1
        Citation Issued: Yes - Following too closely (V.C. 21703)
        
        MEDICAL RECORDS - LA ORTHOPEDICS
        Patient: Jane Doe
        Date of Birth: January 15, 1985
        Date of Service: May 5, 2024
        
        Chief Complaint: Neck and lower back pain following motor vehicle accident
        
        Injuries Identified:
        - Cervical strain (neck)
        - Lumbar strain (lower back)
        - Possible herniated disc at C5-C6
        
        Treatment Plan:
        - Physical therapy (3x per week for 6 weeks)
        - MRI of cervical and lumbar spine
        - Orthopedic consultation
        - Pain management as needed
        
        Treating Physician: Dr. Michael Smith, MD
        """
        
        sample_email_body = """
        Dear Ron,
        
        Please find attached the police report and medical records for our client 
        Jane Doe's auto accident case. 
        
        Our client was rear-ended on May 3, 2024, while stopped at a traffic light 
        on Sunset Boulevard in Los Angeles. The at-fault driver has GEICO insurance, 
        but we have not yet received policy limit information.
        
        Jane has been treating with Dr. Smith at LA Orthopedics. An MRI has been 
        ordered to rule out disc herniation.
        
        Please let me know if you need any additional information.
        
        Best regards,
        Sarah Levine, Esq.
        Levine & Associates
        sarah@levinelaw.com
        """
        
        # Test extraction
        case_data = processor.extract_case_data(sample_pdf_content, sample_email_body)
        
        # Verify extraction results
        print(f"   ✅ Client Name: {case_data.client_name}")
        print(f"   ✅ Date of Loss: {case_data.date_of_loss}")
        print(f"   ✅ Accident Type: {case_data.accident_type}")
        print(f"   ✅ Injuries: {len(case_data.injuries)} found")
        print(f"   ✅ Attorney: {case_data.attorney_name}")
        print(f"   ✅ Location: {case_data.accident_location}")
        
        # Basic validation
        assert case_data.client_name is not None, "Client name should be extracted"
        assert case_data.date_of_loss is not None, "Date of loss should be extracted"
        assert len(case_data.injuries) > 0, "Injuries should be extracted"
        
        print("✅ Case Data Extraction Test Passed")
        return True, case_data
        
    except Exception as e:
        print(f"❌ Case Data Extraction Test Failed: {e}")
        return False, None

def test_missing_information_analysis():
    """Test missing information identification"""
    print("\n🔍 Testing Missing Information Analysis...")
    
    try:
        processor = LegalCaseProcessor()
        
        # Create incomplete case data
        incomplete_case = CaseData(
            client_name="Jane Doe",
            date_of_loss="May 3, 2024",
            accident_type="Auto Accident",
            injuries=["Neck strain", "Back pain"],
            # Missing: policy limits, treatment details, etc.
        )
        
        missing_info = processor.identify_missing_information(incomplete_case)
        
        print(f"   ✅ Found {len(missing_info)} missing information items")
        for i, item in enumerate(missing_info[:5], 1):  # Show first 5
            print(f"   {i}. {item}")
        
        assert len(missing_info) > 0, "Should identify missing information"
        
        print("✅ Missing Information Analysis Test Passed")
        return True
        
    except Exception as e:
        print(f"❌ Missing Information Analysis Test Failed: {e}")
        return False

def test_location_risk_analysis():
    """Test location risk analysis"""
    print("\n🌍 Testing Location Risk Analysis...")
    
    try:
        processor = LegalCaseProcessor()
        
        # Test different locations
        test_locations = [
            "Los Angeles, CA",
            "Houston, TX", 
            "New York, NY",
            "Miami, FL"
        ]
        
        for location in test_locations:
            print(f"   Testing location: {location}")
            analysis = processor.analyze_location_risk(location)
            
            print(f"     Political Leaning: {analysis.political_leaning}")
            print(f"     Tort Environment: {analysis.tort_environment}")
            print(f"     Risk Level: {analysis.risk_level}")
            
            assert analysis.political_leaning is not None, f"Should analyze {location}"
        
        print("✅ Location Risk Analysis Test Passed")
        return True
        
    except Exception as e:
        print(f"❌ Location Risk Analysis Test Failed: {e}")
        return False

def test_attorney_verification():
    """Test attorney verification"""
    print("\n⚖️ Testing Attorney Verification...")
    
    try:
        processor = LegalCaseProcessor()
        
        # Test different attorney scenarios
        test_attorneys = [
            ("Sarah Levine", "sarah@levinelaw.com", "CA"),
            ("John Smith", "john@gmail.com", "TX"),
            ("Maria Garcia", "mgarcia@garcialegal.com", "FL"),
        ]
        
        for name, email, state in test_attorneys:
            print(f"   Testing attorney: {name}")
            verification = processor.verify_attorney(name, email, state)
            
            print(f"     Bar Status: {verification.bar_status}")
            print(f"     Email Verified: {verification.email_verified}")
            print(f"     Professional Domain: {verification.firm_verified}")
            
            assert verification.name == name, "Should preserve attorney name"
        
        print("✅ Attorney Verification Test Passed")
        return True
        
    except Exception as e:
        print(f"❌ Attorney Verification Test Failed: {e}")
        return False

def test_comprehensive_report_generation():
    """Test comprehensive report generation"""
    print("\n📄 Testing Comprehensive Report Generation...")
    
    try:
        processor = LegalCaseProcessor()
        
        # Create sample data
        case_data = CaseData(
            client_name="Jane Doe",
            date_of_loss="May 3, 2024",
            accident_type="Auto Accident",
            injuries=["Cervical strain", "Lumbar strain"],
            treatment=["Physical therapy", "MRI ordered"],
            accident_location="Los Angeles, CA",
            attorney_name="Sarah Levine",
            attorney_email="sarah@levinelaw.com"
        )
        
        missing_info = [
            "• Policy limits not disclosed",
            "• Treatment duration unknown",
            "• Prior injuries/claims history needed"
        ]
        
        # Mock location and attorney analysis
        from legal_case_processor import LocationAnalysis, AttorneyVerification
        
        location_analysis = LocationAnalysis(
            city="Los Angeles",
            state="CA",
            political_leaning="Liberal",
            tort_environment="Tort-Friendly",
            risk_level="High",
            notes="Los Angeles is known for plaintiff-friendly juries"
        )
        
        attorney_verification = AttorneyVerification(
            name="Sarah Levine",
            bar_status="Likely Active",
            email_verified=True,
            firm_verified=True,
            notes="Professional email domain suggests legitimate practice"
        )
        
        # Generate report
        report = processor.generate_comprehensive_report(
            case_data, missing_info, location_analysis, 
            attorney_verification, "sarah@levinelaw.com", "Auto Accident Case - Jane Doe"
        )
        
        # Verify report content
        assert "Jane Doe" in report, "Report should contain client name"
        assert "May 3, 2024" in report, "Report should contain date of loss"
        assert "Los Angeles" in report, "Report should contain location"
        assert "Policy limits" in report, "Report should contain missing info"
        assert "High" in report, "Report should contain risk assessment"
        
        print("   ✅ Report generated successfully")
        print(f"   ✅ Report length: {len(report)} characters")
        print("   ✅ All required sections present")
        
        # Save sample report for review
        with open("sample_legal_case_report.txt", "w") as f:
            f.write(report)
        print("   📄 Sample report saved to: sample_legal_case_report.txt")
        
        print("✅ Comprehensive Report Generation Test Passed")
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive Report Generation Test Failed: {e}")
        return False

def test_legal_case_email_detection():
    """Test legal case email detection"""
    print("\n📧 Testing Legal Case Email Detection...")
    
    try:
        monitor = LegalCaseMonitor()
        
        # Test cases
        test_cases = [
            {
                'subject': 'Auto Accident Case - Jane Doe',
                'body': 'Please find attached medical records and police report for our client.',
                'sender': 'attorney@lawfirm.com',
                'expected': True
            },
            {
                'subject': 'Personal Injury Claim Documentation',
                'body': 'Enclosed are the demand letter and insurance information.',
                'sender': 'sarah@levinelaw.com',
                'expected': True
            },
            {
                'subject': 'Meeting Reminder',
                'body': 'Don\'t forget about our meeting tomorrow at 2 PM.',
                'sender': 'colleague@company.com',
                'expected': False
            },
            {
                'subject': 'Invoice #12345',
                'body': 'Please find attached invoice for services rendered.',
                'sender': 'billing@vendor.com',
                'expected': False
            }
        ]
        
        correct_predictions = 0
        
        for i, test_case in enumerate(test_cases, 1):
            result = monitor.is_legal_case_email(
                test_case['subject'], 
                test_case['body'], 
                test_case['sender']
            )
            
            if result == test_case['expected']:
                correct_predictions += 1
                status = "✅"
            else:
                status = "❌"
            
            print(f"   {status} Test {i}: {test_case['subject'][:30]}... -> {result}")
        
        accuracy = correct_predictions / len(test_cases)
        print(f"   📊 Accuracy: {accuracy:.1%} ({correct_predictions}/{len(test_cases)})")
        
        assert accuracy >= 0.75, "Should achieve at least 75% accuracy"
        
        print("✅ Legal Case Email Detection Test Passed")
        return True
        
    except Exception as e:
        print(f"❌ Legal Case Email Detection Test Failed: {e}")
        return False

def test_full_pipeline():
    """Test the complete legal case processing pipeline"""
    print("\n🔄 Testing Full Legal Case Processing Pipeline...")
    
    try:
        processor = LegalCaseProcessor()
        
        # Sample email data
        email_body = """
        Dear Ron,
        
        I am forwarding the case materials for our client's slip and fall incident.
        The accident occurred at a grocery store in Miami, FL on June 15, 2024.
        
        Our client, Maria Rodriguez, slipped on a wet floor that was not properly marked.
        She suffered a broken wrist and ankle sprain. She has been treating with 
        Dr. Johnson at Miami Orthopedics.
        
        The store's insurance carrier is State Farm, but policy limits are unknown.
        
        Please review and provide your analysis.
        
        Best regards,
        Michael Chen, Esq.
        Chen & Associates
        """
        
        # Mock PDF content
        pdf_content = """
        INCIDENT REPORT
        Date: June 15, 2024
        Location: SuperMart Grocery Store, 123 Main St, Miami, FL
        
        Injured Party: Maria Rodriguez (DOB: 03/22/1978)
        Incident: Slip and fall on wet floor in produce section
        
        Injuries:
        - Fractured right wrist (Colles fracture)
        - Left ankle sprain (Grade 2)
        
        Treatment:
        - Emergency room visit
        - Orthopedic consultation
        - Cast application for wrist
        - Physical therapy referral
        
        Witness: John Doe (Store employee)
        Store Manager: Sarah Wilson
        """
        
        # Process through full pipeline
        report = processor.process_legal_case_email(
            email_body=email_body,
            pdf_attachments=[],  # Would normally contain actual PDF paths
            sender_email="mchen@chenlaw.com",
            subject="Slip and Fall Case - Maria Rodriguez"
        )
        
        # Verify pipeline results
        assert "Maria Rodriguez" in report, "Report should contain client name"
        assert "June 15, 2024" in report, "Report should contain incident date"
        assert "Miami" in report, "Report should contain location"
        assert "slip" in report.lower(), "Report should contain incident type"
        assert "Michael Chen" in report, "Report should contain attorney name"
        
        print("   ✅ Full pipeline executed successfully")
        print("   ✅ All case elements processed")
        print("   ✅ Comprehensive report generated")
        
        # Save full pipeline report
        with open("sample_full_pipeline_report.txt", "w") as f:
            f.write(report)
        print("   📄 Full pipeline report saved to: sample_full_pipeline_report.txt")
        
        print("✅ Full Pipeline Test Passed")
        return True
        
    except Exception as e:
        print(f"❌ Full Pipeline Test Failed: {e}")
        return False

def run_all_tests():
    """Run all legal case processing tests"""
    print("🧪 Legal Case Processing System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Case Data Extraction", test_case_data_extraction),
        ("Missing Information Analysis", test_missing_information_analysis),
        ("Location Risk Analysis", test_location_risk_analysis),
        ("Attorney Verification", test_attorney_verification),
        ("Comprehensive Report Generation", test_comprehensive_report_generation),
        ("Legal Case Email Detection", test_legal_case_email_detection),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if test_name == "Case Data Extraction":
                # Special case for extraction test that returns data
                success, case_data = test_func()
                results[test_name] = success
            else:
                results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} Test Error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(tests)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\n🎯 Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your Legal Case Processing System is ready to use.")
        print("\n🚀 Next Steps:")
        print("   1. Configure your email settings in .env file")
        print("   2. Run: python legal_case_monitor.py")
        print("   3. Send test emails with legal case PDFs")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        
    return passed == total

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        if test_name == "extraction":
            test_case_data_extraction()
        elif test_name == "missing":
            test_missing_information_analysis()
        elif test_name == "location":
            test_location_risk_analysis()
        elif test_name == "attorney":
            test_attorney_verification()
        elif test_name == "report":
            test_comprehensive_report_generation()
        elif test_name == "detection":
            test_legal_case_email_detection()
        elif test_name == "pipeline":
            test_full_pipeline()
        else:
            print("Usage: python test_legal_case_processor.py [extraction|missing|location|attorney|report|detection|pipeline]")
            print("   or: python test_legal_case_processor.py (to run all tests)")
    else:
        run_all_tests()

if __name__ == "__main__":
    main()
