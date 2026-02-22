#!/usr/bin/env python3
"""
Operations Agent
Manages projects, tracks deadlines, identifies bottlenecks
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

class OperationsAgent:
    def __init__(self, vault_path="./vault", skills_dir="./skills", ai_client=None):
        self.vault_path = Path(vault_path)
        self.skills_dir = Path(skills_dir)
        self.ai_client = ai_client  # OpenRouter AI client
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.plans_dir = self.vault_path / "Plans"
        self.active_projects_dir = self.vault_path / "Active_Projects"
        self.done_dir = self.vault_path / "Done"

        # Import skills
        import sys
        sys.path.append(str(self.skills_dir))

        from approval_manager import ApprovalManager
        from audit_logger import AuditLogger
        from dashboard_updater import DashboardUpdater

        self.approval_manager = ApprovalManager(vault_path)
        self.audit_logger = AuditLogger(vault_path)
        self.dashboard_updater = DashboardUpdater(vault_path)

    def monitor_operations_tasks(self):
        """Monitor for new operations-related tasks in Needs_Action"""
        operations_keywords = ['project', 'task', 'deadline', 'schedule', 'bottleneck', 'workflow', 'process', 'operation', 'timeline', 'milestone', 'deliverable']

        operations_tasks = []
        for item in self.needs_action_dir.glob("*.md"):
            content = item.read_text().lower()
            if any(keyword in content for keyword in operations_keywords):
                operations_tasks.append(item)

        return operations_tasks

    def extract_project_info(self, task_file):
        """Extract project information from task content"""
        content = task_file.read_text()

        project_info = {
            'name': task_file.stem,
            'description': content[:200] if len(content) > 200 else content,
            'priority': 'medium',  # Default priority
            'deadline': None,
            'milestones': [],
            'status': 'new',
            'dependencies': [],
            'original_task': task_file.stem
        }

        # Extract information using simple pattern matching
        lines = content.split('\n')
        for line in lines:
            line_lower = line.lower()

            if 'priority:' in line_lower or 'urgent' in line_lower or 'high priority' in line_lower:
                project_info['priority'] = 'high'
            elif 'low priority' in line_lower:
                project_info['priority'] = 'low'

            if 'deadline' in line_lower or 'due' in line_lower:
                # Simple date extraction (would be more sophisticated in real implementation)
                import re
                dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', line)
                if dates:
                    project_info['deadline'] = dates[0]

        return project_info

    def create_project_plan(self, task_file, project_info):
        """Create a project plan with milestones and timeline"""
        plan_content = f"""---
title: "Project Plan: {project_info['name']}"
created: {datetime.now().isoformat()}
project_name: {project_info['name']}
priority: {project_info['priority']}
deadline: {project_info['deadline'] or 'Not specified'}
status: planning
original_task: {project_info['original_task']}
---

# Project Plan: {project_info['name']}

## Project Overview
{project_info['description']}

## Priority
{project_info['priority'].upper()}

## Deadline
{project_info['deadline'] or 'To be determined'}

## Status
{project_info['status']}

## Recommended Actions
1. Break down into specific tasks
2. Assign resources if needed
3. Set up progress tracking
4. Monitor for potential bottlenecks

## Next Steps
- [ ] Review and approve project plan
- [ ] Create detailed task breakdown
- [ ] Set up milestone tracking
- [ ] Assign to active projects

## Risk Assessment
- Timeline: {project_info['deadline'] or 'No deadline set'}
- Resource requirements: [To be determined]
- Dependencies: [To be identified]

## Approval Required
This project plan requires approval before proceeding to implementation phase.
"""

        # Save plan to Plans directory
        plan_path = self.plans_dir / f"project_plan_{project_info['name']}.md"
        plan_path.write_text(plan_content)

        # Also save to Active Projects if it's approved later
        project_path = self.active_projects_dir / f"{project_info['name']}.md"
        project_path.write_text(f"""---
title: "Active Project: {project_info['name']}"
created: {datetime.now().isoformat()}
status: planned
priority: {project_info['priority']}
deadline: {project_info['deadline'] or 'Not specified'}
---

# Active Project: {project_info['name']}

## Description
{project_info['description']}

## Status
Planned - Awaiting approval

## Timeline
- Created: {datetime.now().isoformat()}
- Deadline: {project_info['deadline'] or 'Not specified'}

## Next Steps
- Project plan approval pending
- Task breakdown to follow
- Resource allocation to follow
""")

        self.audit_logger.log_action(
            "PROJECT_PLAN_CREATED",
            f"Created project plan for {project_info['name']}",
            {
                "project_name": project_info['name'],
                "priority": project_info['priority'],
                "deadline": project_info['deadline']
            }
        )

        return plan_path

    def identify_bottlenecks(self):
        """Identify potential bottlenecks in active projects"""
        bottleneck_report = {
            'overdue_projects': [],
            'high_priority_unchanged': [],
            'inactive_projects': []
        }

        # Check all active projects
        for project_file in self.active_projects_dir.glob("*.md"):
            content = project_file.read_text()

            # Look for projects with high priority that haven't changed recently
            if 'priority: high' in content.lower():
                mod_time = datetime.fromtimestamp(project_file.stat().st_mtime)
                if mod_time < datetime.now() - timedelta(days=3):  # No changes in 3 days
                    bottleneck_report['high_priority_unchanged'].append({
                        'project': project_file.name,
                        'last_updated': mod_time.isoformat()
                    })

            # Look for projects with past deadlines
            if project_file.stat().st_mtime < datetime.now().timestamp():
                if 'deadline:' in content:
                    import re
                    dates = re.findall(r'deadline: (.+)', content)
                    for d in dates:
                        if 'past' in d.lower() or ('202' in d and datetime.strptime(d.split()[0], '%Y-%m-%d') < datetime.now() if len(d.split()) > 0 and '/' not in d else False):
                            bottleneck_report['overdue_projects'].append({
                                'project': project_file.name,
                                'deadline': d.strip()
                            })

        # Create bottleneck report if issues found
        if any(bottleneck_report.values()):
            self.create_bottleneck_report(bottleneck_report)

    def create_bottleneck_report(self, bottleneck_report):
        """Create a report on identified bottlenecks"""
        report_content = f"""---
title: "Operations Bottleneck Report"
created: {datetime.now().isoformat()}
report_type: bottleneck_analysis
status: active
---

# Operations Bottleneck Report

## Overview
Analysis of potential bottlenecks in active projects and operations.

## Overdue Projects
"""
        for item in bottleneck_report['overdue_projects']:
            report_content += f"- {item['project']}: Deadline {item['deadline']}\n"

        report_content += f"""
## High Priority Unchanged Projects
Projects marked as high priority with no recent updates:
"""
        for item in bottleneck_report['high_priority_unchanged']:
            report_content += f"- {item['project']}: Last updated {item['last_updated']}\n"

        report_content += f"""
## Inactive Projects
Projects with no recent activity requiring attention:
"""
        for item in bottleneck_report['inactive_projects']:
            report_content += f"- {item['project']}\n"

        report_content += f"""
## Recommendations
1. Review overdue projects for timeline adjustments
2. Check status of high-priority unchanged projects
3. Consider reassigning or escalating blocked projects
4. Update project statuses regularly
"""

        report_path = self.plans_dir / f"bottleneck_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.write_text(report_content)

        self.audit_logger.log_action(
            "BOTTLENECK_REPORT_CREATED",
            "Created bottleneck analysis report",
            {"bottlenecks_found": sum(len(v) for v in bottleneck_report.values())}
        )

    def process_operations_tasks(self):
        """Process all operations-related tasks"""
        operations_tasks = self.monitor_operations_tasks()

        processed_count = 0
        for task in operations_tasks:
            print(f"Processing operations task: {task.name}")

            try:
                project_info = self.extract_project_info(task)
                plan_path = self.create_project_plan(task, project_info)
                print(f"Created project plan: {plan_path.name}")

                # Move original task to avoid re-processing
                completed_path = self.done_dir / f"processed_ops_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task.name}"
                task.rename(completed_path)

                processed_count += 1
            except Exception as e:
                self.audit_logger.log_error(
                    "OPERATIONS_PROCESSING_ERROR",
                    f"Error processing {task.name}: {str(e)}",
                    {"task_file": task.name}
                )

        return processed_count

    def run(self):
        """Main execution method"""
        print(f"Operations Agent starting at {datetime.now()}")

        processed_count = self.process_operations_tasks()
        self.identify_bottlenecks()

        print(f"Operations Agent completed - processed {processed_count} tasks")

        # Update dashboard and run approval manager
        self.dashboard_updater.run("Operations Agent activity")
        self.approval_manager.run()

if __name__ == "__main__":
    agent = OperationsAgent()
    agent.run()