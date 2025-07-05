#!/usr/bin/env python3
"""
Project Management Script for PDF Agent Project

This script helps manage the organized project structure including:
- Running different components
- Managing dependencies
- Running tests
- Deployment operations
"""

import sys
import subprocess
import argparse
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"

def run_command(cmd, cwd=None, check=True):
    """Run a command with error handling"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None, e.stderr, e.returncode

def install_dependencies(component=None):
    """Install dependencies for specified component or all"""
    print("📦 Installing Dependencies...")
    
    if component:
        req_file = CONFIG_DIR / f"{component}_requirements.txt"
        if req_file.exists():
            print(f"Installing dependencies for {component}...")
            _, stderr, code = run_command(f"pip install -r {req_file}")
            if code == 0:
                print(f"✅ {component} dependencies installed successfully")
            else:
                print(f"❌ Failed to install {component} dependencies")
                if stderr:
                    print(f"Error: {stderr}")
        else:
            print(f"❌ Requirements file not found: {req_file}")
    else:
        # Install all requirements
        for req_file in CONFIG_DIR.glob("*requirements.txt"):
            print(f"Installing dependencies from {req_file.name}...")
            _, stderr, code = run_command(f"pip install -r {req_file}")
            if code == 0:
                print(f"✅ {req_file.name} installed successfully")
            else:
                print(f"❌ Failed to install {req_file.name}")
                if stderr:
                    print(f"Error: {stderr}")

def run_tests(component=None):
    """Run tests for specified component or all"""
    print("🧪 Running Tests...")
    
    if component:
        test_file = TESTS_DIR / f"test_{component}.py"
        if test_file.exists():
            print(f"Running tests for {component}...")
            _, stderr, code = run_command(f"python {test_file}")
            if code == 0:
                print(f"✅ {component} tests passed")
            else:
                print(f"❌ {component} tests failed")
                if stderr:
                    print(f"Error: {stderr}")
        else:
            print(f"❌ Test file not found: {test_file}")
    else:
        # Run all tests
        test_files = list(TESTS_DIR.glob("test_*.py"))
        if test_files:
            for test_file in test_files:
                print(f"Running {test_file.name}...")
                _, stderr, code = run_command(f"python {test_file}")
                if code == 0:
                    print(f"✅ {test_file.name} passed")
                else:
                    print(f"❌ {test_file.name} failed")
                    if stderr:
                        print(f"Error: {stderr}")
        else:
            print("❌ No test files found")

def start_service(service):
    """Start a specific service"""
    print(f"🚀 Starting {service}...")
    
    service_map = {
        "core": SRC_DIR / "core" / "pdf_agent.py",
        "email": SRC_DIR / "email_agent" / "email_pdf_agent.py",
        "legal": SRC_DIR / "legal_system" / "legal_case_monitor.py",
        "twitter": SRC_DIR / "twitter_monitor" / "twitter_ai_monitor.py"
    }
    
    if service in service_map:
        service_file = service_map[service]
        if service_file.exists():
            print(f"Starting {service} service...")
            print(f"Command: python {service_file}")
            print("Press Ctrl+C to stop...")
            
            try:
                subprocess.run(f"python {service_file}", shell=True, cwd=PROJECT_ROOT, check=False)
            except KeyboardInterrupt:
                print(f"\n🛑 {service} service stopped")
        else:
            print(f"❌ Service file not found: {service_file}")
    else:
        print(f"❌ Unknown service: {service}")
        print("Available services: core, email, legal, twitter")

def setup_environment():
    """Setup the development environment"""
    print("🔧 Setting up Development Environment...")
    
    # Create necessary directories
    directories = [LOGS_DIR, CONFIG_DIR / "local"]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Setup Python path
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
        print(f"✅ Added {SRC_DIR} to Python path")
    
    # Check for .env file
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found. Creating template...")
        env_template = """# PDF Agent Project Environment Variables
# Copy this file to .env and fill in your values

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration
EMAIL_SERVER=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# Legal Case System
LEGAL_CASE_EMAIL=legal@yourfirm.com

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Twitter/X API (optional)
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
"""
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_template)
        print("✅ Created .env template file")
    
    print("✅ Environment setup complete!")

def show_status():
    """Show project status"""
    print("📊 Project Status")
    print("=" * 50)
    
    # Check components
    components = {
        "Core PDF Agent": SRC_DIR / "core" / "pdf_agent.py",
        "Email Agent": SRC_DIR / "email_agent" / "email_pdf_agent.py",
        "Legal System": SRC_DIR / "legal_system" / "legal_case_processor.py",
        "Twitter Monitor": SRC_DIR / "twitter_monitor" / "twitter_ai_monitor.py"
    }
    
    for name, file_path in components.items():
        status = "✅ Available" if file_path.exists() else "❌ Missing"
        print(f"{name}: {status}")
    
    # Check configuration
    print("\n📋 Configuration Files:")
    config_files = list(CONFIG_DIR.glob("*.py")) + list(CONFIG_DIR.glob("*.txt"))
    for config_file in config_files:
        print(f"  ✅ {config_file.name}")
    
    # Check tests
    print("\n🧪 Test Files:")
    test_files = list(TESTS_DIR.glob("test_*.py"))
    for test_file in test_files:
        print(f"  ✅ {test_file.name}")
    
    # Check logs
    print("\n📝 Log Files:")
    log_files = list(LOGS_DIR.glob("*.log"))
    if log_files:
        for log_file in log_files:
            size = log_file.stat().st_size
            print(f"  📄 {log_file.name} ({size} bytes)")
    else:
        print("  📄 No log files found")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="PDF Agent Project Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_project.py setup              # Setup development environment
  python manage_project.py install            # Install all dependencies
  python manage_project.py install --component email  # Install email dependencies
  python manage_project.py test               # Run all tests
  python manage_project.py test --component legal     # Run legal system tests
  python manage_project.py start core         # Start core PDF agent
  python manage_project.py start email        # Start email agent
  python manage_project.py status             # Show project status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    subparsers.add_parser("setup", help="Setup development environment")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument("--component", help="Install dependencies for specific component")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--component", help="Run tests for specific component")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start a service")
    start_parser.add_argument("service", choices=["core", "email", "legal", "twitter"], 
                            help="Service to start")
    
    # Status command
    subparsers.add_parser("status", help="Show project status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🎯 PDF Agent Project Manager")
    print("=" * 50)
    
    if args.command == "setup":
        setup_environment()
    elif args.command == "install":
        install_dependencies(args.component)
    elif args.command == "test":
        run_tests(args.component)
    elif args.command == "start":
        start_service(args.service)
    elif args.command == "status":
        show_status()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
