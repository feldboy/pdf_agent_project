#!/usr/bin/env python3
"""
Test script for Email PDF Agent

This script helps you test various components of the Email PDF Agent
to ensure everything is working correctly.
"""

import os
import sys
import tempfile
import logging
from pathlib import Path
from email_config import EmailPDFConfig
from email_pdf_agent import EmailPDFAgent

# Configure logging for testing
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_configuration():
    """Test the configuration"""
    print("🔧 Testing Configuration...")
    
    missing = EmailPDFConfig.validate_config()
    
    if missing:
        print("❌ Configuration Test Failed")
        print("Missing required settings:")
        for item in missing:
            print(f"   - {item}")
        return False
    
    print("✅ Configuration Test Passed")
    return True

def test_email_connection():
    """Test email server connections"""
    print("\n📧 Testing Email Connection...")
    
    try:
        # Create agent with test mode
        config = EmailPDFConfig.get_config_dict()
        agent = EmailPDFAgent(config)
        
        # Test IMAP connection
        print("   Testing IMAP connection...")
        mail = agent.connect_to_email()
        
        # Test getting emails (just check connection)
        status, messages = mail.search(None, 'ALL')
        if status == 'OK':
            print(f"   ✅ IMAP connection successful")
            print(f"   📬 Found {len(messages[0].split())} total emails in inbox")
        
        mail.close()
        mail.logout()
        
        print("✅ Email Connection Test Passed")
        return True
        
    except Exception as e:
        print(f"❌ Email Connection Test Failed: {e}")
        return False

def test_llm_connection():
    """Test LLM API connection"""
    print("\n🤖 Testing LLM Connection...")
    
    try:
        config = EmailPDFConfig.get_config_dict()
        agent = EmailPDFAgent(config)
        
        # Test with a simple summarization task
        test_text = """
        This is a test document for the Email PDF Agent.
        The document contains information about testing procedures
        and validation of system components.
        
        Key points:
        1. System testing is important
        2. Configuration validation is required
        3. All components should be tested before deployment
        """
        
        print("   Testing LLM summarization...")
        summary = agent.summarize_text(test_text, "test_document.pdf")
        
        if summary and len(summary) > 50:
            print("   ✅ LLM connection successful")
            print(f"   📄 Generated summary: {len(summary)} characters")
            print(f"   📝 Sample: {summary[:100]}...")
        else:
            raise Exception("Summary too short or empty")
        
        print("✅ LLM Connection Test Passed")
        return True
        
    except Exception as e:
        print(f"❌ LLM Connection Test Failed: {e}")
        return False

def test_pdf_processing():
    """Test PDF text extraction"""
    print("\n📄 Testing PDF Processing...")
    
    try:
        # Create a simple test PDF
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        # Create temporary PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_pdf_path = temp_file.name
        
        # Generate test PDF content
        doc = SimpleDocTemplate(temp_pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        story.append(Paragraph("Test PDF Document", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("This is a test PDF created for validating the Email PDF Agent.", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Key Information:", styles['Heading2']))
        story.append(Paragraph("• PDF processing is working correctly", styles['Normal']))
        story.append(Paragraph("• Text extraction functionality is operational", styles['Normal']))
        story.append(Paragraph("• The system can handle PDF documents", styles['Normal']))
        
        doc.build(story)
        
        # Test PDF processing
        config = EmailPDFConfig.get_config_dict()
        agent = EmailPDFAgent(config)
        
        print("   Testing PDF text extraction...")
        extracted_text = agent.extract_text_from_pdf(temp_pdf_path)
        
        if extracted_text and len(extracted_text) > 50:
            print("   ✅ PDF text extraction successful")
            print(f"   📄 Extracted {len(extracted_text)} characters")
            print(f"   📝 Sample: {extracted_text[:100].replace(chr(10), ' ')}...")
        else:
            raise Exception("Extracted text too short or empty")
        
        # Clean up
        os.unlink(temp_pdf_path)
        
        print("✅ PDF Processing Test Passed")
        return True
        
    except Exception as e:
        print(f"❌ PDF Processing Test Failed: {e}")
        # Clean up on error
        try:
            os.unlink(temp_pdf_path)
        except:
            pass
        return False

def test_email_sending():
    """Test email sending capability"""
    print("\n📤 Testing Email Sending...")
    
    try:
        config = EmailPDFConfig.get_config_dict()
        agent = EmailPDFAgent(config)
        
        # Send test email
        print("   Sending test summary email...")
        
        test_summary = """
        Email PDF Agent Test Summary
        ===========================
        
        This is a test summary generated by the Email PDF Agent
        to verify that email sending functionality is working correctly.
        
        Test completed successfully at: """ + str(os.popen('date').read().strip())
        
        agent._send_summary_email(
            summary=test_summary,
            pdf_filename="test_document.pdf",
            original_sender="test@example.com",
            original_subject="Test Email Subject",
            original_date="Test Date"
        )
        
        print("   ✅ Test email sent successfully")
        print(f"   📧 Check {config['recipient_email']} for the test summary")
        
        print("✅ Email Sending Test Passed")
        return True
        
    except Exception as e:
        print(f"❌ Email Sending Test Failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Email PDF Agent Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Email Connection", test_email_connection),
        ("LLM Connection", test_llm_connection),
        ("PDF Processing", test_pdf_processing),
        ("Email Sending", test_email_sending),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} Test Error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
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
        print("🎉 All tests passed! Your Email PDF Agent is ready to use.")
        print("\n🚀 You can now run: python email_pdf_agent.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the agent.")
        
        # Provide specific guidance
        if not results.get("Configuration", True):
            print("\n📝 Configuration Issues:")
            print("   - Check your .env file")
            print("   - Verify all required environment variables are set")
        
        if not results.get("Email Connection", True):
            print("\n📧 Email Connection Issues:")
            print("   - Verify your email credentials")
            print("   - Check IMAP/SMTP server settings")
            print("   - Ensure 2FA and app passwords are set up correctly")
        
        if not results.get("LLM Connection", True):
            print("\n🤖 LLM Connection Issues:")
            print("   - Check your API key")
            print("   - Verify your API quota/credits")
            print("   - Test your internet connection")

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        if test_name == "config":
            test_configuration()
        elif test_name == "email":
            test_email_connection()
        elif test_name == "llm":
            test_llm_connection()
        elif test_name == "pdf":
            test_pdf_processing()
        elif test_name == "send":
            test_email_sending()
        else:
            print("Usage: python test_email_agent.py [config|email|llm|pdf|send]")
            print("   or: python test_email_agent.py (to run all tests)")
    else:
        run_all_tests()

if __name__ == "__main__":
    main()
