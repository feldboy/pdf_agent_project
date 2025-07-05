#!/usr/bin/env python3
"""
Legal Case Processing System - Main Startup Script

This script provides a complete legal case processing system that monitors emails,
extracts case information from PDFs, performs underwriting analysis, and sends
comprehensive reports.

Usage:
    python legal_case_system.py --mode [monitor|test|demo]
    
Modes:
    monitor: Start continuous email monitoring (production mode)
    test: Run system tests to verify functionality
    demo: Run with sample data to demonstrate capabilities
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from legal_case_monitor import LegalCaseMonitor
from legal_case_processor import LegalCaseProcessor
from legal_case_config import LegalCaseConfig
from test_legal_case_processor import run_all_tests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('legal_case_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print system banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                      LEGAL CASE PROCESSING SYSTEM                           ║
║                                                                              ║
║  📬 Automated Email Processing for Legal Case Analysis                      ║
║  🧠 AI-Powered Case Data Extraction & Underwriting                         ║
║  🌍 Location Risk Analysis & Attorney Verification                         ║
║  📊 Comprehensive Case Reports & Follow-up Recommendations                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_system_requirements():
    """Check if system requirements are met"""
    print("🔍 Checking System Requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"   ✅ Python version: {sys.version}")
    
    # Check required packages
    required_packages = [
        'agno', 'pypdf', 'python-dotenv', 'requests',
        'openai', 'anthropic', 'google-generativeai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install", ' '.join(missing_packages))
        return False
    
    # Check configuration
    print("\n🔧 Checking Configuration...")
    missing_config = LegalCaseConfig.validate_config()
    
    if missing_config:
        print("❌ Configuration incomplete:")
        for item in missing_config:
            print(f"   - {item}")
        print("\n📝 Please create a .env file with required settings")
        print("Run: python legal_case_config.py to create a template")
        return False
    
    print("   ✅ Configuration complete")
    
    print("\n✅ All system requirements met!")
    return True

def run_demo_mode():
    """Run demonstration with sample data"""
    print("\n🎭 Running Legal Case Processing Demo...")
    
    try:
        processor = LegalCaseProcessor()
        
        # Sample legal case email
        demo_email = """
        Dear Ron,
        
        Please find attached case materials for a significant personal injury matter.
        
        Our client, Michael Thompson (DOB: 08/15/1980), was involved in a serious 
        auto accident on Highway 101 in San Francisco, CA on September 15, 2024.
        
        INCIDENT SUMMARY:
        - T-bone collision at intersection of Market St & Van Ness Ave
        - Client had green light, defendant ran red light
        - Client transported by ambulance to UCSF Medical Center
        
        INJURIES:
        - Traumatic brain injury (mild TBI)
        - Fractured ribs (3 ribs, left side)
        - Shoulder separation (Grade 2 AC joint)
        - Ongoing headaches and memory issues
        
        TREATMENT:
        - Emergency room care at UCSF
        - Neurological consultation with Dr. Sarah Kim
        - Orthopedic treatment with Dr. James Liu
        - Physical therapy at Bay Area Sports Medicine
        - Neuropsychological evaluation scheduled
        
        DEFENDANT INFORMATION:
        - Driver: Robert Wilson (commercial delivery truck)
        - Insurance: Travelers Commercial (policy limits unknown)
        - Citation issued for running red light
        
        This appears to be a high-value case given the TBI and ongoing symptoms.
        Client is a software engineer earning $150,000 annually and may have 
        significant lost wage exposure.
        
        Please provide your underwriting analysis and recommendations.
        
        Best regards,
        Jennifer Martinez, Esq.
        Martinez & Associates Personal Injury Law
        jmartinez@martinezlaw.com
        (415) 555-0123
        """
        
        # Sample PDF content (simulated)
        demo_pdf_content = """
        POLICE ACCIDENT REPORT
        Report #: SF-2024-091501
        Date: September 15, 2024
        Time: 3:47 PM
        Location: Market St & Van Ness Ave, San Francisco, CA
        
        VEHICLES INVOLVED:
        Vehicle 1: 2022 Tesla Model 3 (Michael Thompson)
        Vehicle 2: 2019 Ford Transit Van (Robert Wilson - ABC Delivery Co.)
        
        PRELIMINARY INVESTIGATION:
        - Traffic signal functioning normally
        - Vehicle 1 had green light (confirmed by witness)
        - Vehicle 2 entered intersection on red light
        - No evidence of impairment for either driver
        - Road conditions: dry, clear visibility
        
        WITNESS STATEMENTS:
        - Maria Garcia (pedestrian): "The delivery truck definitely ran the red light"
        - John Chen (nearby business owner): "Heard the crash, saw truck had run light"
        
        CITATION ISSUED:
        - Vehicle 2 driver cited for violation of CVC 21453(a) - Red Light
        
        MEDICAL RECORDS - UCSF MEDICAL CENTER
        Patient: Michael Thompson
        DOB: 08/15/1980
        Date of Service: 09/15/2024
        
        EMERGENCY DEPARTMENT REPORT:
        Chief Complaint: Motor vehicle accident with head trauma
        
        EXAMINATION FINDINGS:
        - Glasgow Coma Scale: 14 (mild alteration)
        - CT scan of head: Small contusion, frontal lobe
        - Chest X-ray: Fractures of ribs 4, 5, 6 on left
        - Left shoulder X-ray: AC joint separation, Grade 2
        
        DIAGNOSIS:
        1. Mild traumatic brain injury
        2. Rib fractures x3, left side
        3. Acromioclavicular joint separation, Grade 2
        4. Post-concussion syndrome
        
        TREATMENT:
        - Neurology consultation ordered
        - Pain management protocol initiated
        - Orthopedic referral for shoulder
        - Return for follow-up in 1 week
        - Work restrictions: No driving, cognitive rest
        
        NEUROPSYCHOLOGICAL EVALUATION REPORT
        Patient: Michael Thompson
        Date: 10/01/2024
        Evaluator: Dr. Patricia Wong, PhD
        
        COGNITIVE TESTING RESULTS:
        - Processing speed: 2 standard deviations below norm
        - Working memory: Significantly impaired
        - Executive function: Mild to moderate deficits
        - Attention/concentration: Markedly impaired
        
        FUNCTIONAL IMPACT:
        - Unable to perform complex software engineering tasks
        - Difficulty with multi-tasking and problem-solving
        - Fatigue with cognitive effort
        - Emotional lability and irritability
        
        PROGNOSIS:
        - Some improvement expected over 6-12 months
        - May have permanent cognitive deficits
        - Vocational rehabilitation likely needed
        """
        
        print("   Processing demo case through full pipeline...")
        
        # Process through the complete system
        report = processor.process_legal_case_email(
            email_body=demo_email,
            pdf_attachments=[],  # Simulated PDF content above
            sender_email="jmartinez@martinezlaw.com",
            subject="High-Value TBI Case - Michael Thompson"
        )
        
        print("\n" + "="*80)
        print("📄 DEMO CASE ANALYSIS REPORT")
        print("="*80)
        print(report)
        print("="*80)
        
        # Save demo report
        with open("demo_legal_case_report.txt", "w") as f:
            f.write(report)
        
        print(f"\n📄 Demo report saved to: demo_legal_case_report.txt")
        print("✅ Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Demo mode failed: {e}")
        print(f"❌ Demo failed: {e}")

def run_monitor_mode():
    """Run continuous email monitoring"""
    print("\n📬 Starting Legal Case Email Monitoring...")
    
    try:
        monitor = LegalCaseMonitor()
        
        print("🔄 Monitor is now running...")
        print("📧 Watching for legal case emails...")
        print("⚡ AI analysis will be performed automatically")
        print("📤 Reports will be sent to configured recipient")
        print("\nPress Ctrl+C to stop monitoring")
        
        monitor.start_monitoring()
        
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Monitor mode failed: {e}")
        print(f"❌ Monitoring failed: {e}")

def run_test_mode():
    """Run comprehensive system tests"""
    print("\n🧪 Running Legal Case Processing System Tests...")
    
    success = run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! System is ready for production.")
    else:
        print("\n⚠️  Some tests failed. Please review and fix issues before production use.")
    
    return success

def show_help():
    """Show help information"""
    help_text = """
Legal Case Processing System Help
=================================

OVERVIEW:
This system automatically processes legal case emails, extracts information from PDFs,
performs underwriting analysis, and generates comprehensive reports.

WORKFLOW:
📬 Email Received → 🔍 PDF Analysis → 🧠 AI Processing → 📊 Report Generation → 📤 Email Sent

FEATURES:
• Automatic case data extraction from PDFs and emails
• Underwriting gap analysis with follow-up questions
• Location risk assessment (tort-friendly vs hostile)
• Attorney verification and credibility analysis
• Comprehensive case reports with recommendations

MODES:
• monitor: Continuous email monitoring (production)
• test: Run system validation tests
• demo: Demonstrate with sample case data

SETUP REQUIREMENTS:
1. Python 3.8+ with required packages
2. .env file with email and API configurations
3. Valid OpenAI/Anthropic API key
4. Email account with IMAP/SMTP access

CONFIGURATION:
Run: python legal_case_config.py
This creates a .env template with all required settings.

TESTING:
Run: python legal_case_system.py --mode test
This validates all system components before production use.

PRODUCTION:
Run: python legal_case_system.py --mode monitor
This starts continuous monitoring of your configured email inbox.

For technical support, check the logs:
• legal_case_system.log - Main system log
• legal_case_monitor.log - Email monitoring log
• legal_case_processor.log - Case processing log
    """
    print(help_text)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Legal Case Processing System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python legal_case_system.py --mode monitor    # Start production monitoring
  python legal_case_system.py --mode test       # Run system tests
  python legal_case_system.py --mode demo       # Show demo with sample data
  python legal_case_system.py --help-detailed   # Show detailed help
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['monitor', 'test', 'demo'],
        default='test',
        help='Operating mode (default: test)'
    )
    
    parser.add_argument(
        '--help-detailed',
        action='store_true',
        help='Show detailed help information'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.help_detailed:
        show_help()
        return
    
    # Check system requirements
    if not check_system_requirements():
        print("\n❌ System requirements not met. Please fix issues above.")
        return
    
    # Run requested mode
    if args.mode == 'test':
        success = run_test_mode()
        if success:
            print("\n🚀 System ready! You can now run with --mode monitor")
    
    elif args.mode == 'demo':
        run_demo_mode()
        print("\n🚀 Try running with --mode monitor to start production monitoring")
    
    elif args.mode == 'monitor':
        print("\n⚠️  Production monitoring mode")
        response = input("Are you sure you want to start monitoring? (y/N): ")
        if response.lower() in ['y', 'yes']:
            run_monitor_mode()
        else:
            print("Monitoring cancelled")
    
    print("\n👋 Thank you for using the Legal Case Processing System!")

if __name__ == "__main__":
    main()
