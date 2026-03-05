#!/usr/bin/env python3
"""
Gmail Watcher for AI Employee System
Connects to Gmail using IMAP and checks for new emails every 60 seconds.
Converts new emails into task files and saves them in the incoming/ folder.
"""
import imaplib
import email
from email.header import decode_header
import time
import os
from pathlib import Path
from datetime import datetime
import logging
from dotenv import load_dotenv
import json

load_dotenv()

class GmailWatcher:
    def __init__(self, incoming_path="./incoming", logs_path="./logs"):
        self.email_server = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
        self.email_username = os.getenv("EMAIL_USERNAME")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.incoming_path = Path(incoming_path)
        self.logs_path = Path(logs_path)
        self.last_checked = None

        # Ensure directories exist
        self.incoming_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

        # Setup logging
        log_file = self.logs_path / "gmail_watcher.log"
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

    def connect_to_gmail(self):
        """Connect to Gmail IMAP server"""
        try:
            mail = imaplib.IMAP4_SSL(self.email_server)
            mail.login(self.email_username, self.email_password)
            return mail
        except Exception as e:
            self.logger.error(f"Failed to connect to Gmail: {str(e)}")
            raise

    def get_email_body(self, msg):
        """Extract the body of the email"""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode("utf-8")
                        return body
                    except:
                        continue
        else:
            try:
                body = msg.get_payload(decode=True).decode("utf-8")
                return body
            except:
                return str(msg.get_payload())

    def decode_mime_words(self, s):
        """Decode MIME encoded words in headers"""
        decoded_fragments = decode_header(s)
        decoded_string = ""

        for fragment, encoding in decoded_fragments:
            if isinstance(fragment, bytes):
                if encoding:
                    decoded_string += fragment.decode(encoding)
                else:
                    decoded_string += fragment.decode('utf-8', errors='ignore')
            else:
                decoded_string += fragment

        return decoded_string

    def email_to_task_file(self, email_data):
        """Convert email data to a task file in incoming folder"""
        try:
            subject = self.decode_mime_words(email_data.get("Subject", "No Subject"))
            sender = email_data.get("From", "Unknown Sender")
            date = email_data.get("Date", datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z"))
            body = self.get_email_body(email_data)

            # Create a unique filename based on timestamp and subject
            timestamp = int(time.time())
            safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"email_task_{timestamp}_{safe_subject[:50]}.txt"
            filepath = self.incoming_path / filename

            # Create task content
            task_content = f"""# New Task from Email

## Email Details
- **From**: {sender}
- **Subject**: {subject}
- **Date**: {date}

## Email Content
{body}

## Instructions
Process this email content as a new task in the AI Employee system.
"""

            # Write task file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(task_content)

            self.logger.info(f"Created task file from email: {filename}")
            return filepath

        except Exception as e:
            self.logger.error(f"Failed to create task file from email: {str(e)}")
            return None

    def check_new_emails(self):
        """Check for new emails and convert to task files"""
        try:
            mail = self.connect_to_gmail()

            # Select inbox
            mail.select("inbox")

            # Search for all emails
            status, messages = mail.search(None, "ALL")
            email_ids = messages[0].split()

            # Reverse the list to process newest first
            email_ids = email_ids[::-1]

            # If we don't have a "last checked" time, only process a few recent emails
            if self.last_checked is None:
                email_ids = email_ids[:10]  # Only process last 10 emails on first run

            processed_emails = 0

            for email_id in email_ids:
                # Fetch the email
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                raw_email = msg_data[0][1]

                # Parse the email
                email_message = email.message_from_bytes(raw_email)

                # Check if this email is newer than our last check
                email_date = email_message.get("Date")
                if self.last_checked and email_date:
                    # Convert email date to timestamp for comparison
                    try:
                        email_timestamp = datetime(*email.utils.parsedate(email_date)[:6]).timestamp()
                        if email_timestamp <= self.last_checked:
                            continue  # Skip emails older than last check
                    except:
                        pass  # If parsing fails, process the email anyway

                # Convert email to task file
                task_file = self.email_to_task_file(email_message)
                if task_file:
                    processed_emails += 1

            # Update last checked time to now
            self.last_checked = time.time()

            # Close connection
            mail.close()
            mail.logout()

            if processed_emails > 0:
                self.logger.info(f"Processed {processed_emails} new emails")

            return processed_emails

        except Exception as e:
            self.logger.error(f"Error checking emails: {str(e)}")
            return 0

    def run_watcher(self):
        """Run the Gmail watcher continuously"""
        self.logger.info("Starting Gmail watcher...")
        self.logger.info(f"Monitoring Gmail account: {self.email_username}")

        while True:
            try:
                self.logger.info("Checking for new emails...")
                new_emails = self.check_new_emails()

                if new_emails == 0:
                    self.logger.info("No new emails found")

                # Wait for 60 seconds before checking again
                time.sleep(60)

            except KeyboardInterrupt:
                self.logger.info("Gmail watcher stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in Gmail watcher: {str(e)}")
                # Wait for 60 seconds before retrying
                time.sleep(60)

def main():
    """Main function to run the Gmail watcher"""
    watcher = GmailWatcher()
    watcher.run_watcher()

if __name__ == "__main__":
    main()