#!/usr/bin/env python3
"""
Planning Layer Module for AI Employee System
Generates structured plan files for tasks in Needs_Action directory.
"""
import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class PlanningLayer:
    """Planning layer that generates structured plan files for tasks"""

    def __init__(self, vault_path="./vault"):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.plans_path = self.vault_path / "Plans"
        self.logs_path = Path("logs")

        # Ensure directories exist
        self.plans_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

    def process_needs_action_tasks(self):
        """Process all tasks in Needs_Action directory and generate plans"""
        task_files = list(self.needs_action_path.glob("*.json"))

        if not task_files:
            print(f"No tasks found in {self.needs_action_path}")
            return

        for task_file in task_files:
            self.process_single_task(task_file)

    def process_single_task(self, task_file: Path):
        """Process a single task file and generate a plan"""
        try:
            # Read the task file
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            # Generate plan based on task data
            plan_data = self.generate_plan(task_data)

            # Create plan file
            plan_id = f"plan_{task_data['id']}"
            plan_file_path = self.plans_path / f"{plan_id}.md"

            # Write the plan to file
            with open(plan_file_path, 'w', encoding='utf-8') as f:
                f.write(plan_data)

            # Log the event
            self.log_event(f"Generated plan for task: {task_file.name} -> {plan_file_path.name}")

            # Mark task as processed by moving it to a temporary processed directory
            # or update its status in the JSON file
            self.mark_task_as_processed(task_file, plan_id)

        except Exception as e:
            error_msg = f"Error processing task file {task_file}: {str(e)}"
            print(error_msg)
            self.log_event(error_msg)

    def generate_plan(self, task_data: Dict[str, Any]) -> str:
        """Generate a structured plan based on the task data"""
        # Analyze the task to determine if it requires approval
        requires_approval = self.determine_approval_requirement(task_data)

        # Determine tools required based on task type
        tools_required = self.determine_tools_required(task_data)

        # Perform risk assessment
        risk_assessment = self.perform_risk_assessment(task_data)

        # Create the plan markdown content
        plan_content = f"""# Task Plan: {task_data['title']}

**Plan ID:** {task_data['id']}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Source File:** {task_data.get('source_file', 'N/A')}

## Objective
{self.generate_objective(task_data)}

## Context
{self.generate_context(task_data)}

## Risk Assessment
{risk_assessment}

## Tools Required
{tools_required}

## Dependencies
- [ ] Review and approval if required
- [ ] Any prerequisite information

## Requires Approval
{str(requires_approval).lower()}

## Implementation Steps
1. [ ] Analyze the input data
2. [ ] Execute planned actions
3. [ ] Validate results
4. [ ] Update status

## Success Criteria
- [ ] Task completed successfully
- [ ] Results meet specified requirements
- [ ] Proper documentation created

## Notes
- Generated from file: {task_data.get('source_file', 'N/A')}
- Content preview: {task_data.get('content_preview', 'N/A')[:200]}...
"""

        return plan_content

    def determine_approval_requirement(self, task_data: Dict[str, Any]) -> bool:
        """Determine if the task requires approval based on content and type"""
        # Default to requiring approval for safety
        requires_approval = True

        # Analyze title and content to determine approval requirement
        title = task_data.get('title', '').lower()
        description = task_data.get('description', '').lower()
        content = task_data.get('content_preview', '').lower()

        # If it's a simple informational task, it might not require approval
        if any(keyword in title or keyword in description or keyword in content
               for keyword in ['read', 'view', 'review', 'information', 'note']):
            requires_approval = False

        # If it involves financial or sensitive data, require approval
        if any(keyword in title or keyword in description or keyword in content
               for keyword in ['finance', 'financial', 'money', 'payment', 'salary', 'bank', 'sensitive']):
            requires_approval = True

        # If the task has high priority, require approval
        if task_data.get('priority', 'medium').lower() == 'high':
            requires_approval = True

        return requires_approval

    def determine_tools_required(self, task_data: Dict[str, Any]) -> str:
        """Determine which tools are required for the task"""
        tools = []

        # Determine tools based on file type
        file_type = task_data.get('file_type', '').lower()
        if file_type in ['.json', '.csv', '.xlsx', '.xls']:
            tools.append("- Data processing tools")
        elif file_type in ['.txt', '.md', '.doc', '.docx']:
            tools.append("- Text processing tools")
        elif file_type in ['.jpg', '.png', '.gif', '.pdf']:
            tools.append("- Document/image processing tools")

        # Determine tools based on content
        content = task_data.get('content_preview', '').lower()
        if 'email' in content or 'communication' in content:
            tools.append("- Email communication tools")
        if 'data' in content or 'analysis' in content:
            tools.append("- Data analysis tools")
        if 'report' in content:
            tools.append("- Reporting tools")

        # Add default tools
        tools.extend([
            "- Planning and workflow tools",
            "- Logging and monitoring tools"
        ])

        return "\n".join(tools)

    def perform_risk_assessment(self, task_data: Dict[str, Any]) -> str:
        """Perform risk assessment for the task"""
        risk_assessment = f"""- **Data Sensitivity:** {self.assess_data_sensitivity(task_data)}
- **Security Impact:** {self.assess_security_impact(task_data)}
- **Business Impact:** {self.assess_business_impact(task_data)}
- **Approval Level Required:** {self.assess_approval_level(task_data)}
"""
        return risk_assessment

    def assess_data_sensitivity(self, task_data: Dict[str, Any]) -> str:
        """Assess data sensitivity level"""
        content = task_data.get('content_preview', '').lower()
        if any(keyword in content for keyword in ['password', 'secret', 'confidential', 'private', 'sensitive']):
            return "High - Contains sensitive data"
        elif any(keyword in content for keyword in ['financial', 'payment', 'salary', 'bank']):
            return "Medium-High - Contains financial data"
        else:
            return "Low - Standard business information"

    def assess_security_impact(self, task_data: Dict[str, Any]) -> str:
        """Assess security impact level"""
        content = task_data.get('content_preview', '').lower()
        title = task_data.get('title', '').lower()

        if any(keyword in content or keyword in title for keyword in ['delete', 'remove', 'terminate', 'destroy']):
            return "High - Involves deletion of data/processes"
        elif any(keyword in content or keyword in title for keyword in ['access', 'permission', 'authorization']):
            return "Medium - Involves access controls"
        else:
            return "Low - Standard operations"

    def assess_business_impact(self, task_data: Dict[str, Any]) -> str:
        """Assess business impact level"""
        content = task_data.get('content_preview', '').lower()

        if any(keyword in content for keyword in ['customer', 'client', 'revenue', 'contract']):
            return "Medium-High - Affects customer/business relationships"
        elif any(keyword in content for keyword in ['urgent', 'immediate', 'critical', 'priority']):
            return "High - Critical business operation"
        else:
            return "Low-Medium - Standard business operation"

    def assess_approval_level(self, task_data: Dict[str, Any]) -> str:
        """Assess approval level required"""
        # Based on risk level, determine approval level
        requires_approval = self.determine_approval_requirement(task_data)

        if requires_approval:
            return "Manager or higher approval required"
        else:
            return "Direct execution allowed after review"

    def generate_objective(self, task_data: Dict[str, Any]) -> str:
        """Generate objective based on task data"""
        return f"""Process and complete the task titled "{task_data.get('title', '')}" as described in the incoming file.
Ensure all specified requirements are met and results are documented appropriately."""

    def generate_context(self, task_data: Dict[str, Any]) -> str:
        """Generate context based on task data"""
        return f"""This task originated from an incoming file: {task_data.get('source_file', 'N/A')}.
The file was detected by the file watcher and processed into a structured task.
The original content contains: {task_data.get('content_preview', 'N/A')[:200]}..."""

    def mark_task_as_processed(self, task_file: Path, plan_id: str):
        """Mark the task as processed by updating its status"""
        try:
            # Read the existing task data
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            # Update the status and add plan reference
            task_data['status'] = 'processed'
            task_data['plan_generated'] = plan_id
            task_data['processed_at'] = datetime.now().isoformat()

            # Write back the updated data
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2)

        except Exception as e:
            print(f"Error marking task as processed: {e}")
            self.log_event(f"Error updating task status for {task_file}: {str(e)}")

    def log_event(self, message: str):
        """Log event to system log file"""
        log_file = self.logs_path / "system.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] Planning Layer: {message}\n")


if __name__ == "__main__":
    # For testing purposes
    planner = PlanningLayer()
    planner.process_needs_action_tasks()