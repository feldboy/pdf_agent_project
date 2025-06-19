#!/usr/bin/env python3
"""
Enhanced Email Legal Case Monitor

This script monitors emails for legal case information and processes them
through the comprehensive legal case analysis pipeline.
"""

import os
import time
import logging
import tempfile
import smtplib
import email
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_pdf_agent import EmailPDFAgent  
from legal_case_processor import LegalCaseProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('legal_case_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LegalCaseMonitor(LegalCaseProcessor):
    """Enhanced email monitor for legal case processing"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Legal Case Monitor"""
        super().__init__(config)
        self.processed_emails = set()  # Track processed email UIDs
        
        # Legal case specific keywords for filtering
        self.legal_keywords = [
            'case', 'claim', 'accident', 'injury', 'medical records',
            'police report', 'demand letter', 'settlement', 'litigation',
            'plaintiff', 'defendant', 'attorney', 'lawyer', 'law firm',
            'insurance', 'liability', 'damages', 'auto accident',
            'slip and fall', 'personal injury', 'workers comp'
        ]
        
        logger.info("Legal Case Monitor initialized")
    
    def is_legal_case_email(self, subject: str, body: str, sender: str) -> bool:
        """Determine if email contains legal case information"""
        try:
            # Check subject and body for legal keywords
            content = f"{subject} {body}".lower()
            
            # Count keyword matches
            keyword_matches = sum(1 for keyword in self.legal_keywords if keyword in content)
            
            # Check for law firm domain patterns
            law_firm_domains = ['.law', 'legal', 'attorney', 'lawyer']
            is_law_firm = any(domain in sender.lower() for domain in law_firm_domains)
            
            # Determine if this is likely a legal case email
            is_legal = keyword_matches >= 2 or is_law_firm
            
            if is_legal:
                logger.info(f"Identified legal case email: {keyword_matches} keywords, law firm: {is_law_firm}")
            
            return is_legal
            
        except Exception as e:
            logger.error(f"Error checking if email is legal case: {e}")
            return False
    
    def monitor_and_process(self):
        """Main monitoring loop for legal case emails"""
        logger.info("Starting legal case email monitoring...")
        
        try:
            while self.running:
                try:
                    # Connect to email
                    mail = self.connect_to_email()
                    
                    # Search for unread emails
                    mail.select(self.config['monitor_folder'])
                    status, messages = mail.search(None, 'UNSEEN')
                    
                    if status == 'OK' and messages[0]:
                        email_ids = messages[0].split()
                        logger.info(f"Found {len(email_ids)} unread emails")
                        
                        for email_id in email_ids:
                            try:
                                # Skip if already processed
                                if email_id in self.processed_emails:
                                    continue
                                
                                # Fetch email
                                email_data = self._fetch_email(mail, email_id)
                                if not email_data:
                                    continue
                                
                                subject = email_data.get('subject', '')
                                body = email_data.get('body', '')
                                sender = email_data.get('sender', '')
                                attachments = email_data.get('attachments', [])
                                
                                logger.info(f"Processing email: {subject} from {sender}")
                                
                                # Check if this is a legal case email
                                if not self.is_legal_case_email(subject, body, sender):
                                    logger.info("Email does not appear to contain legal case information, skipping")
                                    self.processed_emails.add(email_id)
                                    continue
                                
                                # Filter for PDF attachments
                                pdf_attachments = [att for att in attachments if att.get('filename', '').lower().endswith('.pdf')]
                                
                                if not pdf_attachments and not any(keyword in body.lower() for keyword in self.legal_keywords[:5]):
                                    logger.info("No PDFs found and no strong legal indicators, skipping")
                                    self.processed_emails.add(email_id)
                                    continue
                                
                                # Save PDF attachments temporarily
                                temp_pdf_paths = []
                                for attachment in pdf_attachments:
                                    temp_path = self._save_temp_attachment(attachment)
                                    if temp_path:
                                        temp_pdf_paths.append(temp_path)
                                
                                # Process the legal case
                                try:
                                    report = self.process_legal_case_email(
                                        email_body=body,
                                        pdf_attachments=temp_pdf_paths,
                                        sender_email=sender,
                                        subject=subject
                                    )
                                    
                                    # Send comprehensive report
                                    self._send_legal_case_report(
                                        report=report,
                                        original_sender=sender,
                                        original_subject=subject,
                                        original_date=email_data.get('date', ''),
                                        pdf_count=len(pdf_attachments)
                                    )
                                    
                                    logger.info("Legal case processed and report sent successfully")
                                    
                                except Exception as e:
                                    logger.error(f"Error processing legal case: {e}")
                                    self._send_error_notification(sender, subject, str(e))
                                
                                finally:
                                    # Clean up temporary files
                                    for temp_path in temp_pdf_paths:
                                        try:
                                            os.unlink(temp_path)
                                        except:
                                            pass
                                
                                # Mark as processed
                                self.processed_emails.add(email_id)
                                
                            except Exception as e:
                                logger.error(f"Error processing email {email_id}: {e}")
                                continue
                    
                    else:
                        logger.debug("No new emails found")
                    
                    # Close email connection
                    try:
                        mail.close()
                        mail.logout()
                    except:
                        pass
                    
                    # Wait before next check
                    if self.running:
                        time.sleep(self.config['check_interval'])
                
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(60)  # Wait longer on error
        
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in monitoring: {e}")
        finally:
            self.running = False
            logger.info("Legal case monitoring stopped")
    
    def _save_temp_attachment(self, attachment: Dict) -> Optional[str]:
        """Save email attachment to temporary file"""
        try:
            filename = attachment.get('filename', 'attachment.pdf')
            content = attachment.get('content', b'')
            
            if not content:
                return None
            
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"legal_case_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
            
            with open(temp_path, 'wb') as f:
                f.write(content)
            
            logger.info(f"Saved attachment to: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Error saving attachment: {e}")
            return None
    
    def _send_legal_case_report(self, report: str, original_sender: str, 
                              original_subject: str, original_date: str, pdf_count: int):
        """Send the comprehensive legal case report"""
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.config['sender_email']
            msg['To'] = self.config['recipient_email']
            msg['Subject'] = f"Legal Case Analysis: {original_subject}"
            
            # Email body with report
            email_body = f"""
Legal Case Analysis Report
==========================

This is an automated analysis of the legal case email received from {original_sender}.

Original Email Details:
- Subject: {original_subject}
- Sender: {original_sender}
- Date: {original_date}
- PDF Attachments: {pdf_count}

{report}

---
This report was generated automatically by the Legal Case Processing Agent.
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['sender_email'], self.config['sender_password'])
                server.send_message(msg)
            
            logger.info(f"Legal case report sent to {self.config['recipient_email']}")
            
        except Exception as e:
            logger.error(f"Error sending legal case report: {e}")
    
    def _send_error_notification(self, original_sender: str, original_subject: str, error_msg: str):
        """Send error notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['sender_email']
            msg['To'] = self.config['recipient_email']
            msg['Subject'] = f"Legal Case Processing Error: {original_subject}"
            
            email_body = f"""
Legal Case Processing Error
===========================

An error occurred while processing the legal case email:

Original Email:
- Subject: {original_subject}
- Sender: {original_sender}

Error Details:
{error_msg}

Please review the email manually or check the system logs.

Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['sender_email'], self.config['sender_password'])
                server.send_message(msg)
            
            logger.info("Error notification sent")
            
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
    
    def start_monitoring(self):
        """Start the monitoring process"""
        self.running = True
        logger.info("Starting legal case email monitoring...")
        self.monitor_and_process()
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.running = False
        logger.info("Stopping legal case email monitoring...")
    
    def _fetch_email(self, mail, email_id):
        """Fetch email data from the server"""
        try:
            # Fetch the email
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status != 'OK':
                logger.error(f"Failed to fetch email {email_id}")
                return None
            
            # Parse the email
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Extract basic information
            subject = msg.get('Subject', '')
            sender = msg.get('From', '')
            date = msg.get('Date', '')
            
            # Extract body
            body = ""
            attachments = []
            
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        except:
                            body += str(part.get_payload())
                    
                    elif "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            attachments.append({
                                'filename': filename,
                                'content': part.get_payload(decode=True)
                            })
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    body = str(msg.get_payload())
            
            return {
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body,
                'attachments': attachments
            }
            
        except Exception as e:
            logger.error(f"Error fetching email {email_id}: {e}")
            return None

def main():
    """Main function"""
    try:
        # Create and start the legal case monitor
        monitor = LegalCaseMonitor()
        
        logger.info("Legal Case Monitor starting...")
        logger.info("Press Ctrl+C to stop monitoring")
        
        monitor.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Error starting monitor: {e}")

if __name__ == "__main__":
    main()
