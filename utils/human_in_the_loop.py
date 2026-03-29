#!/usr/bin/env python3
"""
Human-in-the-Loop Module for AI Employee System
Handles approval workflow for tasks requiring human review.
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class HumanInTheLoop:
    """Handles the approval workflow for tasks requiring human review"""

    def __init__(self, vault_path="./vault", linkedin_poster=None):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.plans_path = self.vault_path / "Plans"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.approved_path = self.vault_path / "Approved"
        self.logs_path = Path("logs")
        self.linkedin_poster = linkedin_poster

        # Ensure directories exist
        self.pending_approval_path.mkdir(exist_ok=True)
        self.approved_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

    def process_plans_for_approval(self):
        """Process all plans in Plans directory and check if they require approval"""
        plan_files = list(self.plans_path.glob("*.md"))

        for plan_file in plan_files:
            # Check if a draft already exists for this plan to avoid duplication
            draft_name = f"draft_{plan_file.stem}.md"
            draft_path = self.pending_approval_path / draft_name

            if draft_path.exists():
                self.log_event(f"Draft already exists for plan {plan_file.name}, skipping")
                continue

            self.process_single_plan(plan_file)

    def process_single_plan(self, plan_file: Path):
        """Process a single plan file and move to appropriate directory if approval is required"""
        try:
            # Read the plan file to check if it requires approval
            requires_approval = self.check_approval_requirement(plan_file)

            if requires_approval:
                # Create a draft action file in Pending_Approval
                draft_file_path = self.create_draft_action(plan_file)
                self.log_event(f"Created draft action for approval: {draft_file_path.name}")

                # Log the event
                self.log_event(f"Plan {plan_file.name} requires approval, draft created in Pending_Approval")
            else:
                # Log that plan doesn't require approval
                self.log_event(f"Plan {plan_file.name} does not require approval")

        except Exception as e:
            error_msg = f"Error processing plan file {plan_file}: {str(e)}"
            print(error_msg)
            self.log_event(error_msg)

    def check_approval_requirement(self, plan_file: Path) -> bool:
        """Check if the plan requires approval by looking for 'Requires Approval' in the plan"""
        with open(plan_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for the "Requires Approval" section in the plan
        lines = content.split('\n')
        for line in lines:
            if line.strip().startswith('## Requires Approval'):
                # Get the next line which should contain the boolean value
                try:
                    next_line_idx = lines.index(line) + 1
                    if next_line_idx < len(lines):
                        approval_line = lines[next_line_idx].strip()
                        return approval_line.lower() == 'true'
                except:
                    pass
        return False

    def create_draft_action(self, plan_file: Path) -> Path:
        """Create a draft action file in Pending_Approval directory based on the plan"""
        # Read the plan file
        with open(plan_file, 'r', encoding='utf-8') as f:
            plan_content = f.read()

        # Create a draft action file name
        draft_file_name = f"draft_{plan_file.stem}.md"
        draft_file_path = self.pending_approval_path / draft_file_name

        # Create draft action content
        draft_content = f"""# Draft Action Plan

**Generated from Plan:** {plan_file.name}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Plan Summary
{plan_content}

## Action Status
- [ ] Pending Approval
- [ ] Ready for Execution (after approval)
- [ ] In Progress
- [ ] Completed

## Approval Section
**Approve this action?**
- [ ] Yes, proceed with execution
- [ ] No, reject this action
- [ ] Modify before approval

**Approver Notes:**
[Add your approval decision and notes here]

## Execution Log
**Execution Steps:**
1. [ ] Review this draft
2. [ ] Make approval decision
3. [ ] Move to Approved folder (to execute) or Rejected folder (to discard)
4. [ ] Monitor execution if approved
"""

        # Write the draft action to file
        with open(draft_file_path, 'w', encoding='utf-8') as f:
            f.write(draft_content)

        return draft_file_path

    def monitor_approved_actions(self):
        """Monitor the Approved directory for actions to execute"""
        # IMPORTANT: This method should NOT be called in normal operation
        # The LinkedInWatcher is responsible for processing approved files
        # to avoid race conditions. This method is kept for legacy compatibility
        # but should not be actively used by the main workflow.
        import warnings
        warnings.warn("monitor_approved_actions should not be called by main workflow - use LinkedInWatcher instead")

        approved_files = list(self.approved_path.glob("*"))

        for approved_file in approved_files:
            self.execute_approved_action(approved_file)

    def execute_approved_action(self, approved_file: Path):
        """Execute an approved action file"""
        try:
            # For now, just log that the action is approved for execution
            # In a real implementation, this would execute the actual action
            self.log_event(f"Executing approved action: {approved_file.name}")

            # Extract task information from the approved file to generate a LinkedIn post
            task_title = "AI Task Completed"
            task_description = "A task was completed by the AI Employee system"

            # Try to extract more meaningful information from the file
            try:
                with open(approved_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Look for plan information in the draft file
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('**Generated from Plan:**'):
                        plan_file = line.split(':')[-1].strip()
                        task_title = f"Completed: {plan_file}"
                        break
                    elif 'Plan Summary' in line:
                        # Look for the next few lines to extract task details
                        for i in range(lines.index(line)+1, min(lines.index(line)+10, len(lines))):
                            if '## Objective' in lines[i]:
                                # Extract the next line which should contain the objective
                                if i+1 < len(lines):
                                    obj_line = lines[i+1].strip()
                                    if obj_line.startswith('#'):
                                        task_description = obj_line[1:].strip()
                                    else:
                                        task_description = obj_line
                                    break
            except Exception as e:
                self.log_event(f"Could not extract task details from {approved_file}: {e}")

            # Note: The LinkedInWatcher module now handles posting to LinkedIn
            # and moving files from Approved to Done after successful posting.
            # The human_in_the_loop no longer moves files to Done to avoid
            # race conditions with the LinkedInWatcher.

            self.log_event(f"Completed execution of task: {approved_file.name}")

        except FileNotFoundError:
            # Handle case where file was removed by another process
            self.log_event(f"File not found when trying to execute: {approved_file.name}")
            # Log but continue processing other files
            return
        except Exception as e:
            error_msg = f"Error executing approved action {approved_file}: {str(e)}"
            print(error_msg)
            self.log_event(error_msg)

    def process_approval_workflow(self):
        """Process the entire approval workflow"""
        # First, process plans that might need approval
        self.process_plans_for_approval()

        # Then, monitor for approved actions to execute
        self.monitor_approved_actions()

    def log_event(self, message: str):
        """Log event to system log file"""
        log_file = self.logs_path / "system.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] Human-in-the-Loop: {message}\n")


if __name__ == "__main__":
    # For testing purposes
    hilt = HumanInTheLoop()
    hilt.process_approval_workflow()