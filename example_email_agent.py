#!/usr/bin/env python3
"""
Example usage of the Email PDF Agent

This script demonstrates how to use the Email PDF Agent programmatically
and shows different configuration options.
"""

import os
import time
import logging
from email_pdf_agent import EmailPDFAgent

def example_basic_usage():
    """Example: Basic usage with default configuration"""
    print("📧 Example 1: Basic Email PDF Agent")
    print("-" * 40)
    
    # The agent will use environment variables or .env file for configuration
    agent = EmailPDFAgent()
    
    print("🤖 Starting agent with default settings...")
    print("💡 Press Ctrl+C to stop")
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")

def example_custom_config():
    """Example: Custom configuration"""
    print("📧 Example 2: Custom Configuration")
    print("-" * 40)
    
    # Custom configuration
    custom_config = {
        # Email settings
        'imap_server': 'imap.gmail.com',
        'imap_port': 993,
        'email_address': os.getenv('EMAIL_ADDRESS'),
        'email_password': os.getenv('EMAIL_PASSWORD'),
        'monitor_folder': 'INBOX',
        
        # SMTP settings
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': os.getenv('SENDER_EMAIL'),
        'sender_password': os.getenv('SENDER_PASSWORD'),
        'recipient_email': os.getenv('RECIPIENT_EMAIL'),
        
        # Processing settings
        'check_interval': 30,  # Check every 30 seconds
        'max_pdf_size': 5242880,  # 5MB limit
        'process_all_pdfs': True,
        
        # LLM settings
        'model_provider': 'openai',
        'model_name': 'gpt-4o-mini',
        'max_tokens': 3000,
        'temperature': 0.1,
        
        # Filtering
        'sender_whitelist': ['trusted@company.com', 'reports@system.com'],
        'subject_keywords': ['report', 'document', 'analysis'],
    }
    
    agent = EmailPDFAgent(custom_config)
    
    print("🤖 Starting agent with custom settings...")
    print(f"⏱️  Check interval: {custom_config['check_interval']} seconds")
    print(f"📊 Max PDF size: {custom_config['max_pdf_size']} bytes")
    print(f"🔍 Sender whitelist: {custom_config['sender_whitelist']}")
    print(f"🏷️  Subject keywords: {custom_config['subject_keywords']}")
    print("💡 Press Ctrl+C to stop")
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")

def example_manual_processing():
    """Example: Manual processing of a single email"""
    print("📧 Example 3: Manual Email Processing")
    print("-" * 40)
    
    # Create agent
    agent = EmailPDFAgent()
    
    print("🔍 Checking for unread emails...")
    
    try:
        # Connect to email
        mail = agent.connect_to_email()
        
        # Get unread emails
        email_ids = agent.get_unread_emails(mail)
        
        if not email_ids:
            print("📭 No unread emails found")
            mail.close()
            mail.logout()
            return
        
        print(f"📬 Found {len(email_ids)} unread emails")
        
        # Process first email as example
        first_email = email_ids[0]
        print(f"📧 Processing email ID: {first_email}")
        
        processed = agent.process_email(mail, first_email)
        
        if processed:
            print("✅ Email processed successfully!")
            # Mark as read
            mail.store(first_email, '+FLAGS', '\\Seen')
        else:
            print("ℹ️  Email did not contain PDF attachments or was filtered out")
        
        mail.close()
        mail.logout()
        
    except Exception as e:
        print(f"❌ Error during manual processing: {e}")

def example_test_summarization():
    """Example: Test the summarization functionality"""
    print("📧 Example 4: Test Summarization")
    print("-" * 40)
    
    # Sample PDF text for testing
    sample_text = """
    QUARTERLY BUSINESS REPORT
    Q2 2025 Performance Summary
    
    Executive Summary:
    This quarter has shown remarkable growth across all business segments.
    Revenue increased by 15% compared to Q1, driven primarily by strong
    performance in the technology and healthcare sectors.
    
    Key Metrics:
    • Total Revenue: $2.5M (up 15% from Q1)
    • Customer Acquisition: 150 new clients
    • Customer Retention Rate: 94%
    • Operating Margin: 22%
    
    Department Performance:
    
    Sales Department:
    - Exceeded targets by 12%
    - Closed 45 major deals
    - Average deal size increased by 8%
    
    Marketing Department:
    - Generated 2,500 qualified leads
    - Launched 3 successful campaigns
    - Social media engagement up 35%
    
    Technology Department:
    - Deployed 2 major product updates
    - Reduced system downtime by 40%
    - Improved API response times by 25%
    
    Challenges and Opportunities:
    While we've seen strong growth, supply chain disruptions continue
    to impact delivery times. We're implementing new logistics partnerships
    to address this issue in Q3.
    
    The AI market presents significant opportunities for expansion,
    with projected 30% growth in demand for our AI-powered solutions.
    
    Outlook for Q3:
    We project continued growth with revenue targets of $2.8M,
    supported by the launch of our new AI product line and
    expansion into European markets.
    
    Recommendations:
    1. Increase investment in supply chain resilience
    2. Accelerate AI product development
    3. Expand European sales team
    4. Implement new customer success programs
    """
    
    # Create agent
    agent = EmailPDFAgent()
    
    print("🤖 Testing summarization with sample business report...")
    
    try:
        # Generate summary
        summary = agent.summarize_text(sample_text, "Q2_Business_Report.pdf")
        
        print("\n📄 Generated Summary:")
        print("=" * 50)
        print(summary)
        print("=" * 50)
        
        print(f"\n📊 Summary length: {len(summary)} characters")
        print("✅ Summarization test completed successfully!")
        
    except Exception as e:
        print(f"❌ Summarization test failed: {e}")

def main():
    """Main function to run examples"""
    
    examples = {
        '1': ('Basic Usage', example_basic_usage),
        '2': ('Custom Configuration', example_custom_config),
        '3': ('Manual Processing', example_manual_processing),
        '4': ('Test Summarization', example_test_summarization),
    }
    
    print("🤖 Email PDF Agent - Examples")
    print("=" * 50)
    print("Choose an example to run:")
    print()
    
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")
    
    print("\nq. Quit")
    print()
    
    while True:
        choice = input("Enter your choice (1-4, q to quit): ").strip().lower()
        
        if choice == 'q':
            print("👋 Goodbye!")
            break
        
        if choice in examples:
            name, func = examples[choice]
            print(f"\n🚀 Running: {name}")
            print("=" * 50)
            
            try:
                func()
            except Exception as e:
                print(f"❌ Example failed: {e}")
            
            print("\n" + "=" * 50)
            input("Press Enter to continue...")
            print()
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
