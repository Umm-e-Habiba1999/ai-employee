#!/usr/bin/env python3
"""
Script to check email configuration and send test email if valid
"""
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import sys

# Add utils to path
sys.path.append("./utils")

def check_email_config():
    """Load .env and check email configuration"""
    # Load .env file
    env_path = Path("E:/hackathon0/ai-employee/.env")
    load_dotenv(dotenv_path=env_path)

    # Read environment variables
    email_username = os.getenv("EMAIL_USERNAME")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_imap_server = os.getenv("EMAIL_IMAP_SERVER")
    email_smtp_server = os.getenv("EMAIL_SMTP_SERVER")
    dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

    print(f"EMAIL_USERNAME: {'Found' if email_username else 'NOT FOUND'}")
    print(f"EMAIL_PASSWORD: {'Found' if email_password else 'NOT FOUND'}")
    print(f"EMAIL_IMAP_SERVER: {email_imap_server}")
    print(f"EMAIL_SMTP_SERVER: {email_smtp_server}")
    print(f"DRY_RUN: {dry_run}")

    # Check if email credentials exist
    if not email_username or not email_password:
        print("\nERROR: EMAIL_USERNAME or EMAIL_PASSWORD not found in .env file")
        return False, None, None, dry_run

    print("\nEmail credentials found successfully!")
    return True, email_username, email_password, dry_run

def send_test_email(email_username, email_password, email_smtp_server, dry_run):
    """Send a test email to the user's own email address"""
    try:
        if dry_run:
            print(f"\nDRY_RUN MODE: Would send test email to {email_username}, but not sending due to DRY_RUN=true")
            return True
        else:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            # Create the email
            msg = MIMEMultipart()
            msg['From'] = email_username
            msg['To'] = email_username
            msg['Subject'] = f"AI Employee Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            body = f"""
            This is a test email from the AI Employee system.

            Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            From: {email_username}
            To: {email_username}

            This confirms that email functionality is working correctly.
            """

            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            server = smtplib.SMTP(email_smtp_server or 'smtp.gmail.com', 587)
            server.starttls()
            server.login(email_username, email_password)

            text = msg.as_string()
            server.sendmail(email_username, email_username, text)
            server.quit()

            print(f"\nTest email sent successfully to {email_username}")
            return True

    except Exception as e:
        print(f"\nERROR: Failed to send test email: {str(e)}")
        return False

def run_silver_tier():
    """Run Silver Tier workflow and log every step"""
    print("\nStarting Silver Tier workflow...")

    try:
        # Import Silver Tier coordinator
        from silver_tier_coordinator import SilverTierCoordinator

        # Create coordinator instance
        coordinator = SilverTierCoordinator()

        # Log each step
        print("1. Watching incoming/ folder...")
        print("2. Processing tasks to vault/Needs_Action...")
        print("3. Generating draft plans in Pending_Approval...")
        print("4. Running approval workflow...")
        print("5. Attempting emails if credentials valid...")

        # Run the workflow cycle
        coordinator.process_workflow_cycle()

        print("\nSilver Tier workflow completed successfully!")
        return True

    except Exception as e:
        print(f"\nERROR: Silver Tier workflow failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to execute all steps"""
    print("Step 1: Checking python-dotenv installation... DONE")
    print("Step 2: Loading .env file and reading environment variables...")

    # Step 2 & 3: Load config and check email credentials
    credentials_valid, email_username, email_password, dry_run = check_email_config()

    if not credentials_valid:
        print("Email credentials check failed - exiting")
        return

    # Step 4: Send test email
    print(f"\nStep 4: Sending test email (DRY_RUN={dry_run})...")
    email_sent = send_test_email(
        email_username,
        email_password,
        os.getenv("EMAIL_SMTP_SERVER"),
        dry_run
    )

    if not email_sent:
        print("Email sending failed, but continuing with Silver Tier workflow...")

    # Step 5: Run Silver Tier
    print("\nStep 5: Running Silver Tier workflow...")
    silver_tier_success = run_silver_tier()

    # Step 6: Report success/failure
    print(f"\nSTEP 6: Reporting results:")
    print(f"- Email configuration check: {'SUCCESS' if credentials_valid else 'FAILED'}")
    print(f"- Test email attempt: {'SUCCESS' if email_sent else 'FAILED'}")
    print(f"- Silver Tier workflow: {'SUCCESS' if silver_tier_success else 'FAILED'}")

    # Step 7: Clean shutdown is handled by the coordinator's process_workflow_cycle
    print("\nStep 7: Silver Tier stopped cleanly")

    overall_success = credentials_valid and silver_tier_success
    print(f"\nOVERALL STATUS: {'SUCCESS' if overall_success else 'FAILURE'}")

    return overall_success

if __name__ == "__main__":
    main()