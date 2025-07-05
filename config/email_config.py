#!/usr/bin/env python3
"""
Configuration for Email PDF Agent

This file contains environment variable definitions and setup instructions
for the automated email-to-PDF processing agent.
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EmailPDFConfig:
    """Configuration class for Email PDF Agent"""
    
    # Email monitoring settings
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
    IMAP_PORT = int(os.getenv('IMAP_PORT', '993'))
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')  # Email to monitor
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # App password
    MONITOR_FOLDER = os.getenv('MONITOR_FOLDER', 'INBOX')
    
    # Email sending settings
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')  # Email to send from
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')  # App password
    RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')  # Where to send summaries
    
    # Processing settings
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds
    MAX_PDF_SIZE = int(os.getenv('MAX_PDF_SIZE', '10485760'))  # 10MB
    PROCESS_ALL_PDFS = os.getenv('PROCESS_ALL_PDFS', 'true').lower() == 'true'
    
    # LLM settings
    MODEL_PROVIDER = os.getenv('MODEL_PROVIDER', 'google')  # google, openai or anthropic
    MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-1.5-flash')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '4000'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.1'))
    
    # Filtering settings (optional)
    SENDER_WHITELIST = os.getenv('SENDER_WHITELIST', '').split(',') if os.getenv('SENDER_WHITELIST') else []
    SUBJECT_KEYWORDS = os.getenv('SUBJECT_KEYWORDS', '').split(',') if os.getenv('SUBJECT_KEYWORDS') else []
    
    @classmethod
    def get_config_dict(cls) -> Dict:
        """Get configuration as dictionary"""
        return {
            'imap_server': cls.IMAP_SERVER,
            'imap_port': cls.IMAP_PORT,
            'email_address': cls.EMAIL_ADDRESS,
            'email_password': cls.EMAIL_PASSWORD,
            'monitor_folder': cls.MONITOR_FOLDER,
            'smtp_server': cls.SMTP_SERVER,
            'smtp_port': cls.SMTP_PORT,
            'sender_email': cls.SENDER_EMAIL,
            'sender_password': cls.SENDER_PASSWORD,
            'recipient_email': cls.RECIPIENT_EMAIL,
            'check_interval': cls.CHECK_INTERVAL,
            'max_pdf_size': cls.MAX_PDF_SIZE,
            'process_all_pdfs': cls.PROCESS_ALL_PDFS,
            'model_provider': cls.MODEL_PROVIDER,
            'model_name': cls.MODEL_NAME,
            'max_tokens': cls.MAX_TOKENS,
            'temperature': cls.TEMPERATURE,
            'sender_whitelist': cls.SENDER_WHITELIST,
            'subject_keywords': cls.SUBJECT_KEYWORDS,
        }
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return list of missing items"""
        missing = []
        
        required_fields = [
            ('EMAIL_ADDRESS', cls.EMAIL_ADDRESS),
            ('EMAIL_PASSWORD', cls.EMAIL_PASSWORD),
            ('SENDER_EMAIL', cls.SENDER_EMAIL),
            ('SENDER_PASSWORD', cls.SENDER_PASSWORD),
            ('RECIPIENT_EMAIL', cls.RECIPIENT_EMAIL),
        ]
        
        for field_name, field_value in required_fields:
            if not field_value:
                missing.append(field_name)
        
        # Check API keys
        if cls.MODEL_PROVIDER == 'openai' and not cls.OPENAI_API_KEY:
            missing.append('OPENAI_API_KEY')
        elif cls.MODEL_PROVIDER == 'anthropic' and not cls.ANTHROPIC_API_KEY:
            missing.append('ANTHROPIC_API_KEY')
        elif cls.MODEL_PROVIDER == 'google' and not cls.GOOGLE_API_KEY:
            missing.append('GOOGLE_API_KEY')
        
        return missing

# Configuration template for .env file
ENV_TEMPLATE = """
# Email PDF Agent Configuration
# Copy this to a .env file and fill in your values

# === EMAIL MONITORING ===
# Email account to monitor for PDF attachments
EMAIL_ADDRESS=your-monitoring-email@gmail.com
EMAIL_PASSWORD=your-app-password-here

# IMAP settings (Gmail defaults)
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
MONITOR_FOLDER=INBOX

# === EMAIL SENDING ===
# Email account to send summaries from (can be same as monitoring email)
SENDER_EMAIL=your-sender-email@gmail.com
SENDER_PASSWORD=your-app-password-here

# Recipient for summary emails
RECIPIENT_EMAIL=your-recipient@gmail.com

# SMTP settings (Gmail defaults)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# === PROCESSING SETTINGS ===
# How often to check for new emails (seconds)
CHECK_INTERVAL=60

# Maximum PDF size to process (bytes, 10MB default)
MAX_PDF_SIZE=10485760

# Process all PDFs in an email or just the first one
PROCESS_ALL_PDFS=true

# === LLM SETTINGS ===
# Model provider: 'openai' or 'anthropic'
MODEL_PROVIDER=openai

# Model name
MODEL_NAME=gpt-4o-mini

# API Keys (set the one you're using)
OPENAI_API_KEY=your-openai-api-key-here
# ANTHROPIC_API_KEY=your-anthropic-api-key-here

# LLM parameters
MAX_TOKENS=4000
TEMPERATURE=0.1

# === FILTERING (OPTIONAL) ===
# Comma-separated list of sender email addresses to process (leave empty for all)
# SENDER_WHITELIST=important@company.com,boss@work.com

# Comma-separated list of subject keywords to look for (leave empty for all)
# SUBJECT_KEYWORDS=report,document,review
"""
