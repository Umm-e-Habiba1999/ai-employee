#!/usr/bin/env python3
"""
Silver Tier Coordinator for AI Employee System
Manages the complete Silver Tier workflow: file watching, planning, approval workflow, and email tools.
"""
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import threading
from dotenv import load_dotenv

from utils.file_watcher import FileWatcher
from utils.planning_layer import PlanningLayer
from utils.human_in_the_loop import HumanInTheLoop
from utils.email_mcp_tool import EmailMCPTool
from utils.gmail_watcher import GmailWatcher

# Load environment variables
load_dotenv()

class SilverTierCoordinator:
    """Coordinates all Silver Tier components"""

    def __init__(self, vault_path="./vault", incoming_path="./incoming"):
        self.vault_path = Path(vault_path)
        self.incoming_path = Path(incoming_path)
        self.logs_path = Path("logs")

        # Initialize all Silver Tier components
        self.file_watcher = FileWatcher(self.incoming_path, self.vault_path)
        self.gmail_watcher = GmailWatcher(self.incoming_path, self.logs_path)
        self.planning_layer = PlanningLayer(self.vault_path)
        self.human_in_loop = HumanInTheLoop(self.vault_path)
        self.email_tool = EmailMCPTool(self.vault_path)

        # Ensure logs directory exists
        self.logs_path.mkdir(exist_ok=True)

        # Thread control
        self.running = False
        self.file_watcher_thread = None
        self.gmail_watcher_thread = None

    def start_file_watcher(self):
        """Start the file watcher in a separate thread"""
        self.file_watcher_thread = threading.Thread(target=self._run_file_watcher, daemon=True)
        self.file_watcher_thread.start()

    def start_gmail_watcher(self):
        """Start the Gmail watcher in a separate thread"""
        self.gmail_watcher_thread = threading.Thread(target=self._run_gmail_watcher, daemon=True)
        self.gmail_watcher_thread.start()

    def _run_file_watcher(self):
        """Internal method to run the file watcher"""
        self.file_watcher.start()
        while self.running:
            time.sleep(1)
        self.file_watcher.stop()

    def _run_gmail_watcher(self):
        """Internal method to run the Gmail watcher"""
        try:
            # Run the Gmail watcher's check once initially, then loop
            while self.running:
                new_emails = self.gmail_watcher.check_new_emails()
                if new_emails > 0:
                    self.log_event(f"Processed {new_emails} new emails from Gmail")
                # Wait 60 seconds before next check
                time.sleep(60)
        except Exception as e:
            self.log_event(f"Error in Gmail watcher: {str(e)}")

    def process_workflow_cycle(self):
        """Run one complete cycle of Silver Tier workflow"""
        self.log_event("Starting Silver Tier workflow cycle")

        try:
            # Process any new files that were detected by the watcher
            # This creates tasks in Needs_Action
            # (The file watcher handles the initial task creation)

            # Process tasks in Needs_Action to generate plans
            self.log_event("Processing needs action tasks for planning")
            self.planning_layer.process_needs_action_tasks()

            # Process plans to determine if approval is needed
            self.log_event("Processing plans for approval workflow")
            self.human_in_loop.process_approval_workflow()

            self.log_event("Silver Tier workflow cycle completed successfully")

        except Exception as e:
            error_msg = f"Error in Silver Tier workflow cycle: {str(e)}"
            print(error_msg)
            self.log_event(error_msg)

    def run_continuous(self, cycle_interval=300):  # Default 5 minutes
        """Run the Silver Tier system continuously"""
        self.log_event("Starting Silver Tier system in continuous mode")

        # Start both the file watcher and Gmail watcher
        self.running = True
        self.start_file_watcher()
        self.start_gmail_watcher()

        try:
            while self.running:
                self.process_workflow_cycle()
                print(f"Waiting {cycle_interval} seconds until next Silver Tier cycle...")
                time.sleep(cycle_interval)
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, shutting down Silver Tier...")
        finally:
            self.running = False
            if self.file_watcher_thread:
                self.file_watcher_thread.join(timeout=5)
            if self.gmail_watcher_thread:
                self.gmail_watcher_thread.join(timeout=5)

        self.log_event("Silver Tier system shutting down")

    def run_once(self):
        """Run the Silver Tier system once and exit"""
        self.log_event("Starting Silver Tier system in single-run mode")

        # Start the file watcher briefly to catch any existing files
        self.file_watcher.start()
        time.sleep(2)  # Brief moment to process any files already in incoming

        # Brief check for new emails
        try:
            new_emails = self.gmail_watcher.check_new_emails()
            if new_emails > 0:
                self.log_event(f"Processed {new_emails} new emails from Gmail")
            time.sleep(2)  # Brief pause to allow email processing
        except Exception as e:
            self.log_event(f"Error checking Gmail: {str(e)}")

        # Process one full cycle
        self.process_workflow_cycle()

        # Stop the file watcher
        self.running = False
        self.file_watcher.stop()

        self.log_event("Silver Tier system completed single run")

    def check_system_status(self) -> Dict[str, Any]:
        """Check and return the status of Silver Tier system"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": os.getenv("DRY_RUN", "false").lower() == "true",
            "components": {
                "file_watcher": {
                    "enabled": True,
                    "incoming_path": str(self.incoming_path),
                    "active": self.file_watcher.observer.is_alive() if hasattr(self.file_watcher.observer, 'is_alive') else False
                },
                "gmail_watcher": {
                    "enabled": True,
                    "incoming_path": str(self.incoming_path),
                    "active": self.gmail_watcher_thread.is_alive() if hasattr(self.gmail_watcher_thread, 'is_alive') and self.gmail_watcher_thread else False,
                    "email_account": self.gmail_watcher.email_username if hasattr(self.gmail_watcher, 'email_username') else None
                },
                "planning_layer": {
                    "enabled": True,
                    "needs_action_path": str(self.needs_action_path),
                    "plans_path": str(self.plans_path)
                },
                "human_in_loop": {
                    "enabled": True,
                    "pending_approval_path": str(self.pending_approval_path),
                    "approved_path": str(self.approved_path)
                },
                "email_tool": {
                    "enabled": True,
                    "configured": self.email_tool.verify_email_config(),
                    "dry_run": self.email_tool.dry_run
                }
            },
            "directories": {
                "incoming_exists": self.incoming_path.exists(),
                "logs_exists": self.logs_path.exists(),
                "needs_action_exists": self.needs_action_path.exists(),
                "plans_exists": self.plans_path.exists(),
                "pending_approval_exists": self.pending_approval_path.exists(),
                "approved_exists": self.approved_path.exists()
            }
        }

        return status

    def process_incoming_tasks(self):
        """Process each file in incoming/ folder into structured tasks under vault/Needs_Action"""
        incoming_files = list(self.incoming_path.glob("*"))

        for incoming_file in incoming_files:
            if incoming_file.is_file() and incoming_file.suffix.lower() != '.tmp':
                self.log_event(f"Processing incoming file: {incoming_file.name}")

                # Process the file using the file watcher's method
                self.file_watcher.event_handler.create_structured_task(str(incoming_file))

    def generate_approval_drafts(self):
        """Generate draft action plans for tasks requiring approval in vault/Pending_Approval"""
        self.planning_layer.process_needs_action_tasks()
        self.human_in_loop.process_plans_for_approval()

    def move_approved_drafts(self):
        """Move approved drafts to vault/Approved when approval is simulated"""
        # Check for any manually approved files in Pending_Approval
        pending_files = list(self.vault_path.joinpath("Pending_Approval").glob("*.md"))

        for pending_file in pending_files:
            # Check if the file has been approved (this is a simplified check)
            with open(pending_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for the approval section and check if it has been approved
            # Check for checked box "[x]" next to "Yes, proceed with execution"
            if "[x] Yes, proceed with execution" in content or "[X] Yes, proceed with execution" in content:
                # Move to Approved folder
                approved_path = self.vault_path / "Approved"
                destination = approved_path / pending_file.name
                import shutil
                shutil.move(str(pending_file), str(destination))
                self.log_event(f"Approved draft moved to Approved folder: {pending_file.name}")

    def send_email_notifications(self, notification_type: str, data: Dict[str, Any]):
        """Send email notifications using test_email_task.py functionality, respecting DRY_RUN mode"""
        # Check DRY_RUN mode
        is_dry_run = os.getenv("DRY_RUN", "false").lower() == "true"

        # Get email credentials from .env
        email_username = os.getenv("EMAIL_USERNAME")
        email_password = os.getenv("EMAIL_PASSWORD")

        if not is_dry_run and email_username and email_password:
            # Real email credentials exist, send actual email
            from test_email_task import EmailTaskHandler

            email_handler = EmailTaskHandler()

            # Create and send specific notification based on type
            if notification_type == "new_task":
                subject = f"New Task Processed: {data.get('task_title', 'Unknown Task')}"
                body = f"""A new task has been processed by the AI Employee system.

Task Title: {data.get('task_title', 'N/A')}
Task ID: {data.get('task_id', 'N/A')}
Source File: {data.get('source_file', 'N/A')}
Processed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: New task processed and added to workflow

Please review if required."""

            elif notification_type == "requires_approval":
                subject = f"Task Requires Approval: {data.get('task_title', 'Unknown Task')}"
                body = f"""A task has been generated that requires your approval.

Task Title: {data.get('task_title', 'N/A')}
Task ID: {data.get('task_id', 'N/A')}
Plan File: {data.get('plan_file', 'N/A')}
Requires Approval: Yes
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please review and approve this task in the Pending_Approval folder."""

            elif notification_type == "task_completed":
                subject = f"Task Completed: {data.get('task_title', 'Unknown Task')}"
                body = f"""A task has been marked as completed.

Task Title: {data.get('task_title', 'N/A')}
Task ID: {data.get('task_id', 'N/A')}
Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Results stored in: Done folder

No further action required."""

            else:
                subject = f"AI Employee System Notification"
                body = f"""System notification from AI Employee.

Type: {notification_type}
Data: {str(data)}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

            # Send email
            success = email_handler.send_test_email(
                recipient=email_username,  # Send to the system admin
                subject=subject,
                body=body
            )

            if success:
                self.log_event(f"Email notification sent successfully: {subject}")
                return {"sent": True, "type": notification_type, "subject": subject}
            else:
                self.log_event(f"Failed to send email notification: {subject}")
                return {"sent": False, "type": notification_type, "subject": subject}
        else:
            # Simulate email sending (DRY_RUN mode or no credentials)
            self.log_event(f"Email notification simulated (DRY_RUN: {is_dry_run}, credentials: {bool(email_username and email_password)}): {notification_type}")
            return {"sent": False, "type": notification_type, "simulated": True, "dry_run": is_dry_run}

    def update_dashboard(self):
        """Update dashboard with current counts: needs_action, in_progress, approval, done_today"""
        import json

        # Count items in each category
        needs_action_count = len(list((self.vault_path / "Needs_Action").glob("*.json")))
        in_progress_count = len(list((self.vault_path / "Plans").glob("*.md")))  # Plans being worked on
        approval_count = len(list((self.vault_path / "Pending_Approval").glob("*.md")))

        # For done_today, count files created today
        from datetime import date, datetime as dt
        today = date.today()
        done_path = self.vault_path / "Done"
        done_today_count = 0

        if done_path.exists():
            for file in done_path.glob("*.md"):
                # Check if file was created today (using datetime conversion)
                file_ctime = dt.fromtimestamp(file.stat().st_ctime).date()
                if file_ctime == today:
                    done_today_count += 1

        # Update dashboard file
        dashboard_file = self.vault_path / "Dashboard.md"

        if dashboard_file.exists():
            with open(dashboard_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update the stats section
            import re
            content = re.sub(
                r"- \*\*Pending Actions\*\*: `\d+`",
                f"- **Pending Actions**: `{needs_action_count}`",
                content
            )
            content = re.sub(
                r"- \*\*Tasks in Progress\*\*: `\d+`",
                f"- **Tasks in Progress**: `{in_progress_count}`",
                content
            )
            content = re.sub(
                r"- \*\*Awaiting Approval\*\*: `\d+`",
                f"- **Awaiting Approval**: `{approval_count}`",
                content
            )
            content = re.sub(
                r"- \*\*Completed Today\*\*: `\d+`",
                f"- **Completed Today**: `{done_today_count}`",
                content
            )

            # Update the last updated timestamp
            content = re.sub(
                r"- \*\*Last Update\*\*: `[\d\-: ]+`",
                f"- **Last Update**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
                content
            )

            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(content)

            self.log_event("Dashboard updated with current counts")
        else:
            self.log_event("Dashboard file not found, creating new one")
            # Create a basic dashboard if it doesn't exist
            dashboard_content = f"""---
title: "AI Employee Dashboard"
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
status: active
---

# AI Employee Dashboard

## System Status
- **Agent**: `RUNNING`
- **Mode**: `LIVE`
- **Last Update**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
- **Connected Services**: `Claude (OpenRouter)`

## Quick Stats
- **Pending Actions**: `{needs_action_count}`
- **Tasks in Progress**: `{in_progress_count}`
- **Awaiting Approval**: `{approval_count}`
- **Completed Today**: `{done_today_count}`

## Today's Plan
```tasks
not done
path includes ./Plans
```

## Recent Activity
```dataview
table status
from "Logs"
sort file.ctime desc
limit 10
```

## Business Goals
```dataview
list
from "Business_Goals.md"
```

## Quick Actions
- [ ] Process new tasks
- [ ] Check pending approvals
- [ ] Generate today's briefing
- [ ] Update dashboard
"""

            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(dashboard_content)

    def process_workflow_cycle(self):
        """Run one complete cycle of Silver Tier workflow"""
        self.log_event("Starting Silver Tier workflow cycle")

        try:
            # 1. Process any new files in incoming folder
            self.log_event("Processing incoming tasks")
            self.process_incoming_tasks()

            # 2. Process tasks in Needs_Action to generate plans
            self.log_event("Processing needs action tasks for planning")
            self.planning_layer.process_needs_action_tasks()

            # 3. Process plans to determine if approval is needed
            self.log_event("Processing plans for approval workflow")
            self.human_in_loop.process_plans_for_approval()

            # 4. Check for approved drafts and move them
            self.log_event("Checking for approved drafts")
            self.move_approved_drafts()

            # 5. Execute any approved actions
            self.log_event("Executing approved actions")
            self.human_in_loop.monitor_approved_actions()

            # 6. Update dashboard with current counts
            self.log_event("Updating dashboard")
            self.update_dashboard()

            self.log_event("Silver Tier workflow cycle completed successfully")

        except Exception as e:
            error_msg = f"Error in Silver Tier workflow cycle: {str(e)}"
            print(error_msg)
            self.log_event(error_msg)
            import traceback
            self.log_event(f"Traceback: {traceback.format_exc()}")

    def log_event(self, message: str):
        """Log event to system log file"""
        log_file = self.logs_path / "system.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] Silver Tier Coordinator: {message}\n")

    @property
    def needs_action_path(self):
        return self.vault_path / "Needs_Action"

    @property
    def plans_path(self):
        return self.vault_path / "Plans"

    @property
    def pending_approval_path(self):
        return self.vault_path / "Pending_Approval"

    @property
    def approved_path(self):
        return self.vault_path / "Approved"


def main():
    """Main function to run the Silver Tier coordinator"""
    import argparse

    parser = argparse.ArgumentParser(description="Silver Tier Coordinator for AI Employee System")
    parser.add_argument("--mode", choices=["once", "continuous"], default="once",
                       help="Run mode: once (single cycle) or continuous (loop)")
    parser.add_argument("--interval", type=int, default=300,
                       help="Cycle interval in seconds (for continuous mode)")
    parser.add_argument("--vault", default="./vault",
                       help="Path to vault directory")
    parser.add_argument("--incoming", default="./incoming",
                       help="Path to incoming directory")

    args = parser.parse_args()

    coordinator = SilverTierCoordinator(vault_path=args.vault, incoming_path=args.incoming)

    if args.mode == "continuous":
        coordinator.run_continuous(cycle_interval=args.interval)
    else:
        coordinator.run_once()


if __name__ == "__main__":
    main()