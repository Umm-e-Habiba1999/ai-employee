#!/usr/bin/env python3
"""
Email MCP Tool Module for AI Employee System
Controlled email sending capability respecting DRY_RUN environment variable.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailMCPTool:
    """Controlled email sending tool that respects DRY_RUN setting"""

    def __init__(self, vault_path="./vault"):
        self.vault_path = Path(vault_path)
        self.logs_path = Path("logs")

        # Ensure logs directory exists
        self.logs_path.mkdir(exist_ok=True)

        # Get settings from environment variables
        self.dry_run = os.getenv("DRY_RUN", "false").lower() == "true"
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.smtp_server = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Send an email with the specified parameters
        Returns a result dictionary with status information
        """
        # Create message ID
        message_id = f"email_{int(datetime.now().timestamp())}"

        # Log the attempt
        self.log_event(f"Email attempt - ID: {message_id}, To: {to_emails}, Subject: {subject}")

        # Check if we're in dry run mode
        if self.dry_run:
            result = self._simulate_email_send(
                to_emails, subject, body, cc_emails, bcc_emails, attachments, message_id
            )
        else:
            # Verify we have necessary credentials
            if not self.email_username or not self.email_password:
                error_msg = "Email credentials not configured. Set EMAIL_USERNAME and EMAIL_PASSWORD in .env"
                self.log_event(f"Email failed - {error_msg}")
                return {
                    "success": False,
                    "message_id": message_id,
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat()
                }

            result = self._actually_send_email(
                to_emails, subject, body, cc_emails, bcc_emails, attachments, message_id
            )

        return result

    def _simulate_email_send(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        message_id: str = None
    ) -> Dict[str, any]:
        """Simulate email sending when DRY_RUN is True"""
        self.log_event(f"DRY_RUN MODE: Email would have been sent (ID: {message_id})")
        self.log_event(f"  To: {to_emails}")
        self.log_event(f"  CC: {cc_emails or []}")
        self.log_event(f"  BCC: {bcc_emails or []}")
        self.log_event(f"  Subject: {subject}")
        self.log_event(f"  Body length: {len(body)} characters")
        self.log_event(f"  Attachments: {len(attachments) if attachments else 0}")

        return {
            "success": True,
            "message_id": message_id,
            "status": "DRY_RUN_SIMULATED",
            "was_sent": False,
            "timestamp": datetime.now().isoformat(),
            "recipient_count": len(to_emails) + (len(cc_emails) if cc_emails else 0) + (len(bcc_emails) if bcc_emails else 0),
            "dry_run": True
        }

    def _actually_send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        message_id: str = None
    ) -> Dict[str, any]:
        """Actually send the email"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            msg['Message-ID'] = f"<{message_id}@ai-employee>"

            # Add CC if provided
            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)

            # Add body to email
            msg.attach(MIMEText(body, 'plain'))

            # Establish connection and send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable encryption
            server.login(self.email_username, self.email_password)

            # Prepare recipient list (to, cc, bcc)
            all_recipients = to_emails[:]
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)

            # Send the email
            text = msg.as_string()
            server.sendmail(self.email_username, all_recipients, text)
            server.quit()

            self.log_event(f"Email sent successfully (ID: {message_id})")

            return {
                "success": True,
                "message_id": message_id,
                "status": "SENT",
                "was_sent": True,
                "timestamp": datetime.now().isoformat(),
                "recipient_count": len(all_recipients),
                "dry_run": False
            }

        except Exception as e:
            error_msg = f"Failed to send email (ID: {message_id}): {str(e)}"
            self.log_event(error_msg)

            return {
                "success": False,
                "message_id": message_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "dry_run": False
            }

    def send_bulk_emails(self, email_list: List[Dict]) -> List[Dict]:
        """
        Send multiple emails in bulk
        Each item in email_list should be a dict with keys: to, subject, body
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

    def verify_email_config(self) -> bool:
        """Verify that email configuration is valid"""
        return bool(self.email_username and self.email_password and self.smtp_server)

    def log_event(self, message: str):
        """Log event to system log file"""
        log_file = self.logs_path / "system.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] Email MCP Tool: {message}\n")


# Example usage and testing function
def test_email_send():
    """Test function to demonstrate email sending"""
    email_tool = EmailMCPTool()

    # Example email
    result = email_tool.send_email(
        to_emails=["recipient@example.com"],
        subject="Test Email from AI Employee",
        body="This is a test email sent by the AI Employee system."
    )

    print(f"Email send result: {result}")


if __name__ == "__main__":
    # For testing purposes
    test_email_send()