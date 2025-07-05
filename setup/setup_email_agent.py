#!/usr/bin/env python3
"""
Setup script for Email PDF Agent

This script helps you set up and configure the Email PDF Agent.
"""

import os
import sys
from pathlib import Path
from email_config import EmailPDFConfig, ENV_TEMPLATE

def create_env_file():
    """Create a .env template file"""
    env_path = Path('.env')
    
    if env_path.exists():
        response = input("🤔 .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("📝 You can manually edit your existing .env file")
            return
    
    print("📝 Creating .env template file...")
    
    with open(env_path, 'w') as f:
        f.write(ENV_TEMPLATE)
    
    print(f"✅ Created {env_path}")
    print("📋 Please edit this file with your actual configuration values")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'agno',
        'pypdf',
        'openai',
        'anthropic',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def validate_configuration():
    """Validate the current configuration"""
    print("\n🔧 Validating configuration...")
    
    missing = EmailPDFConfig.validate_config()
    
    if missing:
        print("❌ Missing required configuration:")
        for item in missing:
            print(f"   - {item}")
        print("\n📝 Please update your .env file or set environment variables")
        return False
    
    print("✅ Configuration is valid")
    return True

def show_gmail_setup_instructions():
    """Show Gmail setup instructions"""
    print("""
📧 Gmail Setup Instructions:

1. Enable 2-Factor Authentication:
   - Go to Google Account settings
   - Security → 2-Step Verification → Turn on

2. Generate App Passwords:
   - Security → 2-Step Verification → App passwords
   - Select app: Mail
   - Select device: Other (custom name) → "Email PDF Agent"
   - Copy the generated 16-character password

3. Use App Password:
   - Use your regular Gmail address for EMAIL_ADDRESS and SENDER_EMAIL
   - Use the app password (not your regular password) for EMAIL_PASSWORD and SENDER_PASSWORD

4. Enable Less Secure Apps (if needed):
   - Some accounts may need to allow less secure apps
   - Go to Google Account → Security → Less secure app access → Turn on

📨 IMAP Settings for Gmail:
   - IMAP Server: imap.gmail.com
   - Port: 993
   - Security: SSL

📤 SMTP Settings for Gmail:
   - SMTP Server: smtp.gmail.com
   - Port: 587
   - Security: TLS
""")

def show_usage_instructions():
    """Show usage instructions"""
    print("""
🚀 Usage Instructions:

1. Basic Usage:
   python email_pdf_agent.py

2. Testing:
   - Send an email with a PDF attachment to your monitoring email
   - The agent will process it and send a summary to your recipient email

3. Monitoring:
   - Check the email_pdf_agent.log file for activity logs
   - The agent will log all processing steps and errors

4. Stopping:
   - Press Ctrl+C to stop the agent gracefully

⚙️ Configuration Options:

- CHECK_INTERVAL: How often to check for new emails (seconds)
- MAX_PDF_SIZE: Maximum PDF size to process (bytes)
- SENDER_WHITELIST: Only process emails from specific senders
- SUBJECT_KEYWORDS: Only process emails with specific keywords in subject

🔧 Troubleshooting:

- If emails aren't being processed, check the log file
- Verify your email credentials and IMAP/SMTP settings
- Make sure PDFs aren't too large (default max: 10MB)
- Check if emails are being marked as read properly
""")

def main():
    """Main setup function"""
    print("🤖 Email PDF Agent Setup")
    print("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Create .env file
    print("\n" + "=" * 50)
    create_env_file()
    
    # Show Gmail setup instructions
    print("\n" + "=" * 50)
    show_gmail_setup_instructions()
    
    # Wait for user to configure
    input("\n⏳ Press Enter after you've configured your .env file...")
    
    # Validate configuration
    print("\n" + "=" * 50)
    config_ok = validate_configuration()
    
    # Show usage instructions
    print("\n" + "=" * 50)
    show_usage_instructions()
    
    # Final status
    print("\n" + "=" * 50)
    if deps_ok and config_ok:
        print("🎉 Setup complete! You can now run:")
        print("   python email_pdf_agent.py")
    else:
        print("⚠️  Setup incomplete. Please fix the issues above.")
        if not deps_ok:
            print("   - Install missing dependencies")
        if not config_ok:
            print("   - Complete configuration in .env file")

if __name__ == "__main__":
    main()
