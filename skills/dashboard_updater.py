#!/usr/bin/env python3
"""
Dashboard Updater Skill
Updates Dashboard.md with recent activity
"""

import os
import json
from datetime import datetime, date
from pathlib import Path

class DashboardUpdater:
    def __init__(self, vault_path="./vault"):
        self.vault_path = Path(vault_path)
        self.dashboard_path = self.vault_path / "Dashboard.md"
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.plans_dir = self.vault_path / "Plans"
        self.pending_approval_dir = self.vault_path / "Pending_Approval"
        self.done_dir = self.vault_path / "Done"
        self.logs_dir = self.vault_path / "Logs"

    def get_counts(self):
        """Get current counts for dashboard"""
        needs_action_count = len(list(self.needs_action_dir.glob("*.md")))
        plans_count = len(list(self.plans_dir.glob("*.md")))
        approval_count = len(list(self.pending_approval_dir.glob("*.md")))

        # Count items in Done directory for today
        today = date.today().strftime("%Y-%m-%d")
        done_today_count = len(list(self.done_dir.glob(f"*{today}*.md")))

        return {
            'needs_action_count': needs_action_count,
            'in_progress_count': plans_count,  # Plans represent in-progress tasks
            'approval_count': approval_count,
            'done_today_count': done_today_count,
        }

    def update_dashboard(self):
        """Update the dashboard with current statistics"""
        counts = self.get_counts()

        # Read current dashboard
        current_dashboard = self.dashboard_path.read_text()

        # Update the specific sections with current values
        updated_dashboard = current_dashboard.replace(
            "- **Last Update**: `{{date}}`",
            f"- **Last Update**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
        )
        updated_dashboard = updated_dashboard.replace(
            "- **Pending Actions**: `{{needs_action_count}}`",
            f"- **Pending Actions**: `{counts['needs_action_count']}`"
        )
        updated_dashboard = updated_dashboard.replace(
            "- **Tasks in Progress**: `{{in_progress_count}}`",
            f"- **Tasks in Progress**: `{counts['in_progress_count']}`"
        )
        updated_dashboard = updated_dashboard.replace(
            "- **Awaiting Approval**: `{{approval_count}}`",
            f"- **Awaiting Approval**: `{counts['approval_count']}`"
        )
        updated_dashboard = updated_dashboard.replace(
            "- **Completed Today**: `{{done_today_count}}`",
            f"- **Completed Today**: `{counts['done_today_count']}`"
        )

        # Write updated dashboard
        self.dashboard_path.write_text(updated_dashboard)
        print(f"Dashboard updated with current counts: {counts}")

    def add_recent_activity(self, activity_description):
        """Add a recent activity entry to the dashboard"""
        activity_entry = f"""
### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {activity_description}
"""

        # In a more sophisticated implementation, we'd insert this in the right place
        # For now, we'll just ensure the dashboard is updated with the latest counts
        self.update_dashboard()

    def run(self, activity_description="System update", ai_mode=None, connected_services=None):
        """Main execution method"""
        print(f"Dashboard Updater starting at {datetime.now()}")

        # Update dashboard with AI status if provided
        if ai_mode is not None or connected_services is not None:
            self.update_dashboard_with_ai_status(ai_mode, connected_services)
        else:
            self.update_dashboard()

        self.add_recent_activity(activity_description)
        print("Dashboard Updater completed")

    def update_dashboard_with_ai_status(self, ai_mode, connected_services):
        """Update dashboard with specific AI mode and connected services"""
        counts = self.get_counts()

        # Read current dashboard
        current_dashboard = self.dashboard_path.read_text()

        # Update the specific sections with current values
        if ai_mode:
            updated_dashboard = current_dashboard.replace(
                "- **Mode**: `DRY_RUN` (default for safety)",
                f"- **Mode**: `{ai_mode}`"
            )
        else:
            updated_dashboard = current_dashboard

        if connected_services is not None:
            updated_dashboard = updated_dashboard.replace(
                "- **Connected Services**: `None`",
                f"- **Connected Services**: `{connected_services}`"
            )

        updated_dashboard = updated_dashboard.replace(
            "- **Last Update**: `{{date}}`",
            f"- **Last Update**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
        )
        updated_dashboard = updated_dashboard.replace(
            "- **Pending Actions**: `{{needs_action_count}}`",
            f"- **Pending Actions**: `{counts['needs_action_count']}`"
        )
        updated_dashboard = updated_dashboard.replace(
            "- **Tasks in Progress**: `{{in_progress_count}}`",
            f"- **Tasks in Progress**: `{counts['in_progress_count']}`"
        )
        updated_dashboard = updated_dashboard.replace(
            "- **Awaiting Approval**: `{{approval_count}}`",
            f"- **Awaiting Approval**: `{counts['approval_count']}`"
        )
        updated_dashboard = updated_dashboard.replace(
            "- **Completed Today**: `{{done_today_count}}`",
            f"- **Completed Today**: `{counts['done_today_count']}`"
        )

        # Write updated dashboard
        self.dashboard_path.write_text(updated_dashboard)
        print(f"Dashboard updated with current counts: {counts} and AI status: Mode={ai_mode}, Services={connected_services}")

if __name__ == "__main__":
    updater = DashboardUpdater()
    updater.run("Initial dashboard update")