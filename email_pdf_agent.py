#!/usr/bin/env python3
"""
Automated Email-to-PDF Processing Agent

This agent monitors emails for PDF attachments, extracts text, summarizes using LLM,
and sends summaries back via email.

Features:
- Email monitoring (IMAP)
- PDF text extraction
- LLM summarization
- Automated email responses
- Error handling and logging
"""

import os
import time
import logging
import smtplib
import imaplib
import email
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pypdf
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.models.google import Gemini
try:
    from config import PDFAgentConfig
except ImportError:
    # Fallback if config.py doesn't exist
    PDFAgentConfig = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_pdf_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailPDFAgent:
    """Automated Email-to-PDF Processing Agent"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Email PDF Agent"""
        self.config = config or self._load_default_config()
        self.agent = self._create_summarization_agent()
        self.running = False
        
        # Validate configuration
        self._validate_config()
        
        logger.info("Email PDF Agent initialized")
    
    def _load_default_config(self) -> Dict:
        """Load default configuration"""
        return {
            # Email monitoring settings
            'imap_server': os.getenv('IMAP_SERVER', 'imap.gmail.com'),
            'imap_port': int(os.getenv('IMAP_PORT', '993')),
            'email_address': os.getenv('EMAIL_ADDRESS'),
            'email_password': os.getenv('EMAIL_PASSWORD'),  # App password for Gmail
            'monitor_folder': os.getenv('MONITOR_FOLDER', 'INBOX'),
            
            # Email sending settings
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL'),
            'sender_password': os.getenv('SENDER_PASSWORD'),
            'recipient_email': os.getenv('RECIPIENT_EMAIL'),
            
            # Processing settings
            'check_interval': int(os.getenv('CHECK_INTERVAL', '60')),  # seconds
            'max_pdf_size': int(os.getenv('MAX_PDF_SIZE', '10485760')),  # 10MB
            'process_all_pdfs': os.getenv('PROCESS_ALL_PDFS', 'true').lower() == 'true',
            
            # LLM settings
            'model_provider': os.getenv('MODEL_PROVIDER', 'openai'),  # openai or anthropic
            'model_name': os.getenv('MODEL_NAME', 'gpt-4o-mini'),
            'max_tokens': int(os.getenv('MAX_TOKENS', '4000')),
            'temperature': float(os.getenv('TEMPERATURE', '0.1')),
            
            # Filtering settings
            'sender_whitelist': os.getenv('SENDER_WHITELIST', '').split(',') if os.getenv('SENDER_WHITELIST') else [],
            'subject_keywords': os.getenv('SUBJECT_KEYWORDS', '').split(',') if os.getenv('SUBJECT_KEYWORDS') else [],
        }
    
    def _validate_config(self):
        """Validate configuration settings"""
        required_fields = [
            'email_address', 'email_password', 'sender_email', 
            'sender_password', 'recipient_email'
        ]
        
        for field in required_fields:
            if not self.config.get(field):
                raise ValueError(f"Missing required configuration: {field}")
        
        # Check API keys
        if self.config['model_provider'] == 'openai' and not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY is required for OpenAI models")
        elif self.config['model_provider'] == 'anthropic' and not os.getenv('ANTHROPIC_API_KEY'):
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic models")
        elif self.config['model_provider'] == 'google' and not os.getenv('GOOGLE_API_KEY'):
            raise ValueError("GOOGLE_API_KEY is required for Google models")
    
    def _create_summarization_agent(self) -> Agent:
        """Create an agent for PDF summarization"""
        
        # Choose model based on provider
        if self.config['model_provider'] == 'openai':
            model = OpenAIChat(
                id=self.config['model_name'],
                max_tokens=self.config['max_tokens'],
                temperature=self.config['temperature']
            )
        elif self.config['model_provider'] == 'anthropic':
            model = Claude(
                id=self.config['model_name'],
                max_tokens=self.config['max_tokens'],
                temperature=self.config['temperature']
            )
        elif self.config['model_provider'] == 'google':
            model = Gemini(
                id=self.config['model_name'],
                temperature=self.config['temperature']
            )
        else:
            raise ValueError(f"Unsupported model provider: {self.config['model_provider']}")
        
        agent = Agent(
            name="PDF Summarization Agent",
            model=model,
            instructions=[
                "You are an expert at summarizing PDF documents.",
                "Create clear, concise, and informative summaries.",
                "Focus on key points, main ideas, and important details.",
                "Structure your summary with clear headings and bullet points when appropriate.",
                "If the document is technical, explain complex concepts simply.",
                "Include the document's purpose, main findings, and conclusions.",
                "Keep summaries between 200-500 words unless the document is very short or very long.",
                "If the text is unclear or incomplete, mention this in your summary.",
            ],
            markdown=True,
        )
        
        return agent
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text
                
            if not text.strip():
                raise ValueError("No text content found in PDF")
            
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def summarize_text(self, text: str, filename: str = "") -> str:
        """Summarize text using the LLM agent"""
        try:
            # Prepare the prompt
            prompt = f"""Please summarize the following document content:

**Document:** {filename}

**Content:**
{text}

**Instructions:**
- Provide a comprehensive yet concise summary
- Highlight key points and main ideas
- Structure the summary clearly
- Include the document's purpose and main conclusions
"""
            
            # Get summary from agent
            summary = self.agent.run(prompt)
            
            logger.info(f"Successfully generated summary for {filename}")
            return summary.content if hasattr(summary, 'content') else str(summary)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise
    
    def connect_to_email(self) -> imaplib.IMAP4_SSL:
        """Connect to email server"""
        try:
            mail = imaplib.IMAP4_SSL(self.config['imap_server'], self.config['imap_port'])
            mail.login(self.config['email_address'], self.config['email_password'])
            mail.select(self.config['monitor_folder'])
            
            logger.info(f"Connected to email server: {self.config['imap_server']}")
            return mail
            
        except Exception as e:
            logger.error(f"Error connecting to email server: {e}")
            raise
    
    def get_unread_emails(self, mail: imaplib.IMAP4_SSL) -> List[bytes]:
        """Get unread emails from the server"""
        try:
            status, messages = mail.search(None, 'UNSEEN')
            if status != 'OK':
                raise Exception("Failed to search for unread emails")
            
            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} unread emails")
            return email_ids
            
        except Exception as e:
            logger.error(f"Error getting unread emails: {e}")
            return []
    
    def process_email(self, mail: imaplib.IMAP4_SSL, email_id: bytes) -> bool:
        """Process a single email for PDF attachments"""
        try:
            # Fetch email
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status != 'OK':
                return False
            
            # Parse email
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Extract email details
            sender = email_message['From']
            subject = email_message['Subject'] or "No Subject"
            date = email_message['Date']
            
            logger.info(f"Processing email from {sender}: {subject}")
            
            # Check filters
            if not self._should_process_email(sender, subject):
                logger.info(f"Email filtered out: {sender} - {subject}")
                return False
            
            # Look for PDF attachments
            pdf_attachments = self._extract_pdf_attachments(email_message)
            
            if not pdf_attachments:
                logger.info("No PDF attachments found")
                return False
            
            # Process each PDF attachment
            for pdf_data, pdf_filename in pdf_attachments:
                try:
                    self._process_pdf_attachment(
                        pdf_data, pdf_filename, sender, subject, date
                    )
                except Exception as e:
                    logger.error(f"Error processing PDF {pdf_filename}: {e}")
                    self._send_error_notification(pdf_filename, str(e), sender, subject)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing email {email_id}: {e}")
            return False
    
    def _should_process_email(self, sender: str, subject: str) -> bool:
        """Check if email should be processed based on filters"""
        # Check sender whitelist
        if self.config['sender_whitelist']:
            sender_allowed = any(
                allowed_sender in sender.lower() 
                for allowed_sender in self.config['sender_whitelist']
            )
            if not sender_allowed:
                return False
        
        # Check subject keywords
        if self.config['subject_keywords']:
            subject_match = any(
                keyword.lower() in subject.lower()
                for keyword in self.config['subject_keywords']
            )
            if not subject_match:
                return False
        
        return True
    
    def _extract_pdf_attachments(self, email_message) -> List[Tuple[bytes, str]]:
        """Extract PDF attachments from email"""
        pdf_attachments = []
        
        for part in email_message.walk():
            if part.get_content_disposition() == 'attachment':
                filename = part.get_filename()
                if filename and filename.lower().endswith('.pdf'):
                    pdf_data = part.get_payload(decode=True)
                    
                    # Check file size
                    if len(pdf_data) > self.config['max_pdf_size']:
                        logger.warning(f"PDF {filename} too large ({len(pdf_data)} bytes)")
                        continue
                    
                    pdf_attachments.append((pdf_data, filename))
                    logger.info(f"Found PDF attachment: {filename}")
        
        return pdf_attachments
    
    def _process_pdf_attachment(self, pdf_data: bytes, filename: str, 
                              sender: str, subject: str, date: str):
        """Process a single PDF attachment"""
        
        # Save PDF to temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_data)
            temp_pdf_path = temp_file.name
        
        try:
            # Extract text from PDF
            pdf_text = self.extract_text_from_pdf(temp_pdf_path)
            
            # Generate summary
            summary = self.summarize_text(pdf_text, filename)
            
            # Send summary email
            self._send_summary_email(summary, filename, sender, subject, date)
            
            logger.info(f"Successfully processed PDF: {filename}")
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_pdf_path)
            except:
                pass
    
    def _send_summary_email(self, summary: str, pdf_filename: str, 
                          original_sender: str, original_subject: str, original_date: str):
        """Send summary email to recipient"""
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.config['sender_email']
            msg['To'] = self.config['recipient_email']
            msg['Subject'] = f"PDF Summary: {pdf_filename}"
            
            # Email body
            email_body = f"""
PDF Summary Report
==================

**Original Email Details:**
- From: {original_sender}
- Subject: {original_subject}
- Date: {original_date}
- PDF File: {pdf_filename}

**Summary:**
{summary}

---
This summary was generated automatically by the Email PDF Agent.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['sender_email'], self.config['sender_password'])
                server.send_message(msg)
            
            logger.info(f"Summary email sent for {pdf_filename}")
            
        except Exception as e:
            logger.error(f"Error sending summary email: {e}")
            raise
    
    def _send_error_notification(self, pdf_filename: str, error_message: str,
                               original_sender: str, original_subject: str):
        """Send error notification email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['sender_email']
            msg['To'] = self.config['recipient_email']
            msg['Subject'] = f"Error Processing PDF: {pdf_filename}"
            
            email_body = f"""
PDF Processing Error
===================

**Error Details:**
- PDF File: {pdf_filename}
- Original Sender: {original_sender}
- Original Subject: {original_subject}
- Error: {error_message}
- Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The PDF could not be processed. Please check the file manually.

---
This notification was generated automatically by the Email PDF Agent.
"""
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['sender_email'], self.config['sender_password'])
                server.send_message(msg)
            
            logger.info(f"Error notification sent for {pdf_filename}")
            
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
    
    def run(self):
        """Main execution loop"""
        logger.info("Starting Email PDF Agent...")
        self.running = True
        
        while self.running:
            try:
                # Connect to email server
                mail = self.connect_to_email()
                
                # Get unread emails
                email_ids = self.get_unread_emails(mail)
                
                # Process each email
                for email_id in email_ids:
                    if not self.running:
                        break
                    
                    try:
                        processed = self.process_email(mail, email_id)
                        if processed:
                            # Mark as read
                            mail.store(email_id, '+FLAGS', '\\Seen')
                    except Exception as e:
                        logger.error(f"Error processing email {email_id}: {e}")
                
                # Close email connection
                mail.close()
                mail.logout()
                
                # Wait before next check
                if self.running:
                    logger.info(f"Waiting {self.config['check_interval']} seconds before next check...")
                    time.sleep(self.config['check_interval'])
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, stopping...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                if self.running:
                    time.sleep(60)  # Wait before retrying
    
    def stop(self):
        """Stop the agent"""
        logger.info("Stopping Email PDF Agent...")
        self.running = False

def main():
    """Main function to run the Email PDF Agent"""
    
    # Create and run the agent
    try:
        agent = EmailPDFAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\n👋 Email PDF Agent stopped by user")
    except Exception as e:
        logger.error(f"Failed to start Email PDF Agent: {e}")
        print(f"❌ Error: {e}")
        print("\n📋 Please check your configuration and try again.")

if __name__ == "__main__":
    main()
