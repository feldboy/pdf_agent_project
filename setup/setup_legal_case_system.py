#!/usr/bin/env python3
"""
Legal Case Processing System Setup Script

This script helps you set up the Legal Case Processing System step by step.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print setup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   LEGAL CASE PROCESSING SYSTEM SETUP                        ║
║                                                                              ║
║  🚀 Get your AI-powered legal case analysis system running in minutes!      ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required. You have {sys.version}")
        print("Please upgrade Python and try again.")
        return False
    
    print(f"✅ Python {sys.version} - Compatible!")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing required packages...")
    
    packages = [
        "agno",
        "pypdf",
        "python-dotenv", 
        "requests",
        "openai",
        "reportlab"  # For testing
    ]
    
    try:
        for package in packages:
            print(f"   Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
        
        print("✅ All packages installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        print("Try running: pip install -r legal_requirements.txt")
        return False

def create_env_file():
    """Create environment configuration file"""
    print("\n⚙️ Setting up configuration...")
    
    env_template = """# Legal Case Processing System Configuration
# Fill in your actual values below

# Email Settings (Gmail recommended)
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=ron@yourcompany.com

# IMAP/SMTP Settings (Gmail default)
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

# API Keys (required)
OPENAI_API_KEY=your-openai-api-key-here
# ANTHROPIC_API_KEY=your-anthropic-key-here (alternative)
# GOOGLE_API_KEY=your-google-key-here (alternative)

# Processing Settings
MAX_PDF_SIZE=20971520
"""
    
    env_path = Path(".env")
    
    if env_path.exists():
        response = input("📄 .env file already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("📄 Keeping existing .env file")
            return True
    
    with open(env_path, 'w') as f:
        f.write(env_template)
    
    print("✅ Created .env configuration file")
    print("📝 Please edit .env and fill in your actual values:")
    print(f"   - Email credentials (Gmail app passwords recommended)")
    print(f"   - OpenAI API key")
    print(f"   - Recipient email address")
    
    return True

def run_demo():
    """Run the system demo"""
    print("\n🎭 Running system demo...")
    
    try:
        subprocess.run([sys.executable, "demo_legal_case_system.py"], check=True)
        print("✅ Demo completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Demo failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Demo script not found. Make sure you're in the correct directory.")
        return False

def show_next_steps():
    """Show next steps for the user"""
    print("\n🎯 Setup Complete! Next Steps:")
    print("=" * 60)
    
    steps = [
        "1. 📧 Configure Email:",
        "   • Create Gmail app password (recommended)",
        "   • Update .env file with email credentials",
        "",
        "2. 🔑 Get OpenAI API Key:",
        "   • Visit: https://platform.openai.com/api-keys", 
        "   • Create API key and add credits",
        "   • Update OPENAI_API_KEY in .env file",
        "",
        "3. ✅ Test the System:",
        "   • Run: python legal_case_system.py --mode test",
        "   • Fix any configuration issues",
        "",
        "4. 🎭 Try the Demo:",
        "   • Run: python legal_case_system.py --mode demo",
        "   • See sample case analysis",
        "",
        "5. 🚀 Start Production:",
        "   • Run: python legal_case_system.py --mode monitor",
        "   • Forward legal case emails to monitored inbox",
        "   • Receive AI analysis reports automatically!",
        "",
        "📚 Documentation:",
        "   • Read: LEGAL_CASE_SYSTEM_README.md",
        "   • For help: python legal_case_system.py --help-detailed",
    ]
    
    for step in steps:
        print(step)

def main():
    """Main setup function"""
    print_banner()
    
    # Step 1: Check Python version
    if not check_python_version():
        return
    
    # Step 2: Install dependencies
    if not install_dependencies():
        print("\n⚠️  Dependency installation failed.")
        print("You can try manually: pip install -r legal_requirements.txt")
        response = input("Continue setup anyway? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            return
    
    # Step 3: Create configuration
    if not create_env_file():
        return
    
    # Step 4: Run demo (optional)
    response = input("\n🎭 Run system demo now? (Y/n): ")
    if response.lower() not in ['n', 'no']:
        run_demo()
    
    # Step 5: Show next steps
    show_next_steps()
    
    print("\n🎉 Setup complete! Your Legal Case Processing System is ready.")
    print("💡 Tip: Start with the demo mode to see the system in action!")

if __name__ == "__main__":
    main()
