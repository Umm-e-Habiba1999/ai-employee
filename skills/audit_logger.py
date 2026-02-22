#!/usr/bin/env python3
"""
Audit Logger Skill
Writes structured logs to /Logs/YYYY-MM-DD.json
"""

import os
import json
from datetime import datetime, date
from pathlib import Path

class AuditLogger:
    def __init__(self, vault_path="./vault"):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / "Logs"

    def get_today_log_path(self):
        """Get the path for today's log file"""
        today = date.today().strftime("%Y-%m-%d")
        return self.logs_dir / f"{today}.json"

    def log_action(self, action_type, description, details=None, status="completed"):
        """Log an action with timestamp and details"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "description": description,
            "status": status,
            "details": details or {}
        }

        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Get today's log file
        log_path = self.get_today_log_path()

        # Read existing log entries or create new list
        if log_path.exists():
            with open(log_path, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = []

        # Add new entry
        log_data.append(log_entry)

        # Write back to file
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        print(f"Logged action: {action_type} - {description}")

    def log_error(self, error_type, error_message, context=None):
        """Log an error with timestamp and context"""
        self.log_action(
            action_type="ERROR",
            description=error_message,
            details={
                "error_type": error_type,
                "context": context or {},
                "status": "error"
            },
            status="error"
        )

    def log_security_event(self, event_type, description, details=None):
        """Log a security-related event"""
        self.log_action(
            action_type=f"SECURITY_{event_type.upper()}",
            description=description,
            details=details or {},
            status="security"
        )

    def run_test_log(self):
        """Create a test log entry to verify functionality"""
        self.log_action(
            "SYSTEM_START",
            "Audit Logger initialized",
            {
                "system": "AI Employee",
                "version": "Bronze Tier",
                "module": "AuditLogger"
            }
        )

    def run(self):
        """Main execution method"""
        print(f"Audit Logger starting at {datetime.now()}")
        self.run_test_log()
        print("Audit Logger initialized and ready")

if __name__ == "__main__":
    logger = AuditLogger()
    logger.run()