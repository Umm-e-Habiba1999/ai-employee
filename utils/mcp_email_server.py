#!/usr/bin/env python3
"""
MCP Email Server for AI Employee System
Provides SMTP-based email sending functionality using credentials from .env file.
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path
import logging
from dotenv import load_dotenv

load_dotenv()

class MCPEmailServer:
    def __init__(self, logs_path="./logs"):
        self.smtp_server = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.logs_path = Path(logs_path)

        # Ensure logs directory exists
        self.logs_path.mkdir(exist_ok=True)

        # Setup logging
        log_file = self.logs_path / "email_server.log"
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

    def send_email(self, to_emails, subject, body, cc_emails=None, bcc_emails=None, attachments=None):
        """
        Send an email using SMTP with credentials from .env file.

        Args:
            to_emails (list): List of recipient email addresses
            subject (str): Email subject
            body (str): Email body
            cc_emails (list, optional): CC recipients
            bcc_emails (list, optional): BCC recipients
            attachments (list, optional): List of file paths to attach

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

            # Add attachments if provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
                    else:
                        self.logger.warning(f"Attachment file not found: {file_path}")

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

    def send_bulk_emails(self, email_list):
        """
        Send multiple emails in bulk.

        Args:
            email_list (list): List of email data dictionaries
                              Each dict should have: to, subject, body keys

        Returns:
            list: Results for each email sent
        """
        results = []
        for email_data in email_list:
            result = self.send_email(
                to_emails=email_data.get("to", []),
                subject=email_data.get("subject", ""),
                body=email_data.get("body", ""),
                cc_emails=email_data.get("cc"),
                bcc_emails=email_data.get("bcc"),
                attachments=email_data.get("attachments")
            )
            results.append(result)
        return results

    def test_connection(self):
        """Test the SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            server.quit()
            self.logger.info("SMTP connection test successful")
            return True
        except Exception as e:
            error_msg = f"SMTP connection test failed: {str(e)}"
            self.logger.error(error_msg)
            return False

def main():
    """Main function to test the email server"""
    server = MCPEmailServer()

    print("Testing SMTP connection...")
    if server.test_connection():
        print("Connection test passed!")

        # Example email
        print("\nSending test email...")
        result = server.send_email(
            to_emails=[server.email_username],  # Send to self
            subject="MCP Email Server Test",
            body="This is a test email from the MCP Email Server."
        )

        print(f"Result: {result}")
    else:
        print("Connection test failed!")

if __name__ == "__main__":
    main()