#!/usr/bin/env python3
"""
MCP Email Server for AI Employee System
Provides an email sending service using SMTP with credentials from .env file.
This is a simple server implementation for the AI Employee system.
"""
import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import logging
from dotenv import load_dotenv
import threading
import time
import queue

load_dotenv()

class EmailMCPService:
    """
    MCP Email Service that provides email sending functionality through a queue-based system.
    This simulates the MCP server functionality for sending emails.
    """
    def __init__(self, logs_path="./logs"):
        self.smtp_server = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.logs_path = Path(logs_path)
        self.email_queue = queue.Queue()
        self.running = False

        # Ensure logs directory exists
        self.logs_path.mkdir(exist_ok=True)

        # Setup logging
        log_file = self.logs_path / "email_mcp_service.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Check if email credentials are provided
        if not self.email_username or not self.email_password:
            self.logger.error("Email credentials not found in .env file")
            raise ValueError("EMAIL_USERNAME and EMAIL_PASSWORD must be set in .env file")

    def send_email(self, to_emails, subject, body, cc_emails=None, bcc_emails=None):
        """
        Send an email using SMTP with credentials from .env file.

        Args:
            to_emails (list): List of recipient email addresses
            subject (str): Email subject
            body (str): Email body
            cc_emails (list, optional): CC recipients
            bcc_emails (list, optional): BCC recipients

        Returns:
            dict: Result of the email sending operation
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject

            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)

            # Add body to email
            msg.attach(MIMEText(body, 'plain'))

            # Prepare recipient list
            all_recipients = to_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)

            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable encryption
            server.login(self.email_username, self.email_password)

            # Send email
            text = msg.as_string()
            server.sendmail(self.email_username, all_recipients, text)
            server.quit()

            result = {
                "success": True,
                "message": f"Email sent successfully to {len(all_recipients)} recipients",
                "recipients": all_recipients,
                "subject": subject,
                "timestamp": datetime.now().isoformat()
            }

            self.logger.info(f"Email sent successfully: {subject}")
            return result

        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            self.logger.error(error_msg)

            result = {
                "success": False,
                "error": str(e),
                "subject": subject,
                "timestamp": datetime.now().isoformat()
            }

            return result

    def queue_email(self, to_emails, subject, body, cc_emails=None, bcc_emails=None):
        """Add an email to the queue for sending"""
        email_data = {
            "to_emails": to_emails,
            "subject": subject,
            "body": body,
            "cc_emails": cc_emails,
            "bcc_emails": bcc_emails,
            "timestamp": time.time()
        }

        self.email_queue.put(email_data)
        self.logger.info(f"Email queued: {subject}")
        return {"queued": True, "subject": subject}

    def process_email_queue(self):
        """Process emails in the queue"""
        processed = 0
        while not self.email_queue.empty():
            try:
                email_data = self.email_queue.get_nowait()
                result = self.send_email(
                    email_data["to_emails"],
                    email_data["subject"],
                    email_data["body"],
                    email_data["cc_emails"],
                    email_data["bcc_emails"]
                )
                processed += 1
                self.logger.info(f"Processed queued email: {result.get('message', 'Unknown')}")
            except queue.Empty:
                break
            except Exception as e:
                self.logger.error(f"Error processing queued email: {str(e)}")

        return processed

    def start_service(self):
        """Start the email service"""
        self.running = True
        self.logger.info("Email MCP Service started")

        # In a real implementation, this would run as a server
        # For now, we'll just process the queue when called
        while self.running:
            try:
                processed = self.process_email_queue()
                if processed > 0:
                    self.logger.info(f"Processed {processed} emails from queue")

                # Check queue every 10 seconds
                time.sleep(10)
            except KeyboardInterrupt:
                self.running = False
                self.logger.info("Email MCP Service stopped by user")
            except Exception as e:
                self.logger.error(f"Error in email service: {str(e)}")
                time.sleep(10)

    def stop_service(self):
        """Stop the email service"""
        self.running = False
        self.logger.info("Email MCP Service stopped")

    def get_queue_status(self):
        """Get the status of the email queue"""
        return {
            "queue_size": self.email_queue.qsize(),
            "running": self.running,
            "smtp_server": self.smtp_server,
            "email_username": self.email_username,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Main function to run the Email MCP Service"""
    import argparse

    parser = argparse.ArgumentParser(description="Email MCP Service for AI Employee System")
    parser.add_argument("--logs", default="./logs", help="Path to logs directory")

    args = parser.parse_args()

    service = EmailMCPService(logs_path=args.logs)

    print("Starting Email MCP Service...")
    print(f"Connected to: {service.smtp_server} as {service.email_username}")
    print("Press Ctrl+C to stop the service")

    try:
        service.start_service()
    except KeyboardInterrupt:
        print("\nStopping Email MCP Service...")
        service.stop_service()

if __name__ == "__main__":
    main()