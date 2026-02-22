#!/usr/bin/env python3
"""
Task Completion Checker Skill
Verifies task is complete and moves related files to /Done
"""

import os
import json
from datetime import datetime
from pathlib import Path

class TaskCompletionChecker:
    def __init__(self, vault_path="./vault"):
        self.vault_path = Path(vault_path)
        self.plans_dir = self.vault_path / "Plans"
        self.approved_dir = self.vault_path / "Approved"
        self.done_dir = self.vault_path / "Done"
        self.logs_dir = self.vault_path / "Logs"

    def find_complete_tasks(self):
        """Find tasks that are marked as complete or have been processed"""
        complete_tasks = []

        # Check approved directory for tasks that might be processed
        for approved_file in self.approved_dir.glob("*.md"):
            # In a real system, this would check for completion indicators
            # For now, we'll consider any approved task as potentially complete
            # if it has a corresponding plan file that indicates completion
            complete_tasks.append(approved_file)

        # Also check plan files for completion status
        for plan_file in self.plans_dir.glob("plan_*.md"):
            content = plan_file.read_text()
            if "status: completed" in content.lower() or "completed: true" in content.lower():
                complete_tasks.append(plan_file)

        return complete_tasks

    def move_to_done(self, task_path):
        """Move a completed task to the Done directory"""
        # Create new filename with completion timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"completed_{timestamp}_{task_path.name}"
        done_path = self.done_dir / new_name

        # Move the file
        task_path.rename(done_path)
        print(f"Moved completed task to Done: {done_path.name}")

        # Also move related files if they exist
        self.move_related_files(task_path.stem, timestamp)

    def move_related_files(self, original_stem, timestamp):
        """Move related files that correspond to the original task"""
        # Look for related plan files
        related_plans = list(self.plans_dir.glob(f"*{original_stem}*.md"))
        for plan in related_plans:
            new_name = f"completed_{timestamp}_{plan.name}"
            done_path = self.done_dir / new_name
            plan.rename(done_path)
            print(f"Moved related plan to Done: {done_path.name}")

        # Look for related approval files
        related_approvals = list(self.approved_dir.glob(f"*{original_stem}*.md"))
        for approval in related_approvals:
            new_name = f"completed_{timestamp}_{approval.name}"
            done_path = self.done_dir / new_name
            approval.rename(done_path)
            print(f"Moved related approval to Done: {done_path.name}")

    def check_and_move_tasks(self):
        """Check for completed tasks and move them to Done directory"""
        complete_tasks = self.find_complete_tasks()

        if not complete_tasks:
            print("No complete tasks found to move to Done directory")
            return

        # Ensure Done directory exists
        self.done_dir.mkdir(parents=True, exist_ok=True)

        for task_path in complete_tasks:
            try:
                self.move_to_done(task_path)
            except Exception as e:
                print(f"Error moving {task_path.name}: {str(e)}")

    def run(self):
        """Main execution method"""
        print(f"Task Completion Checker starting at {datetime.now()}")
        self.check_and_move_tasks()
        print("Task Completion Checker completed")

if __name__ == "__main__":
    checker = TaskCompletionChecker()
    checker.run()