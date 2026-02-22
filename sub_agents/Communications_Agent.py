
#!/usr/bin/env python3
"""
Communications Agent
Handles Gmail + WhatsApp, drafts replies, requires approval for sending
"""

import os
import json
from datetime import datetime
from pathlib import Path

class CommunicationsAgent:
    def __init__(self, vault_path="./vault", skills_dir="./skills", ai_client=None):
        self.vault_path = Path(vault_path)
        self.skills_dir = Path(skills_dir)
        self.ai_client = ai_client  # OpenRouter AI client
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.plans_dir = self.vault_path / "Plans"

        # Import skills
        import sys
        sys.path.append(str(self.skills_dir))

        from inbox_processor import InboxProcessor
        from approval_manager import ApprovalManager
        from audit_logger import AuditLogger

        self.inbox_processor = InboxProcessor(vault_path)
        self.approval_manager = ApprovalManager(vault_path)
        self.audit_logger = AuditLogger(vault_path)

    def monitor_communications(self):
        """Monitor for new communication tasks in Needs_Action"""
        communication_keywords = ['email', 'gmail', 'whatsapp', 'message', 'communication', 'reply', 'response']

        communication_tasks = []
        for item in self.needs_action_dir.glob("*.md"):
            content = item.read_text().lower()
            if any(keyword in content for keyword in communication_keywords):
                communication_tasks.append(item)

        return communication_tasks

    def draft_reply(self, task_file):
        """Draft a reply based on the communication task"""
        content = task_file.read_text()

        # Simple pattern matching for reply drafting
        if 'email' in content.lower() or 'gmail' in content.lower():
            communication_type = 'EMAIL'
        elif 'whatsapp' in content.lower():
            communication_type = 'WHATSAPP'
        else:
            communication_type = 'GENERAL_COMMUNICATION'

        # Create a draft reply based on content
        draft_content = f"""---
title: "Draft Reply for {task_file.stem}"
created: {datetime.now().isoformat()}
original_task: {task_file.stem}
communication_type: {communication_type}
status: drafted
requires_approval: true
---

# Draft Reply

## Original Request
{content[:300]}...

## Suggested Response
Based on the request, here is a suggested response:

[AI-GENERATED RESPONSE WOULD GO HERE]

## Recipient
[RECIPIENT IDENTIFIED FROM CONTEXT]

## Communication Channel
{communication_type}

## Approval Required
- [ ] Send this communication
- [ ] Modify before sending
- [ ] Do not send

## Context
- Original task: {task_file.stem}
- Generated on: {datetime.now().isoformat()}
- Requires human approval before sending
"""

        # Save draft to Plans directory
        draft_path = self.plans_dir / f"draft_reply_{task_file.stem}.md"
        draft_path.write_text(draft_content)

        self.audit_logger.log_action(
            "COMMUNICATION_DRAFT_CREATED",
            f"Created draft reply for {task_file.stem}",
            {"task_id": task_file.stem, "communication_type": communication_type}
        )

        return draft_path

    def process_communication_tasks(self):
        """Process all communication-related tasks"""
        communication_tasks = self.monitor_communications()

        processed_count = 0
        for task in communication_tasks:
            print(f"Processing communication task: {task.name}")

            try:
                draft_path = self.draft_reply(task)
                print(f"Created draft: {draft_path.name}")

                # Move original task to avoid re-processing
                done_dir = self.vault_path / "Done"
                done_dir.mkdir(parents=True, exist_ok=True)
                completed_path = done_dir / f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task.name}"
                task.rename(completed_path)

                processed_count += 1
            except Exception as e:
                self.audit_logger.log_error(
                    "COMMUNICATION_PROCESSING_ERROR",
                    f"Error processing {task.name}: {str(e)}",
                    {"task_file": task.name}
                )

        return processed_count

    def run(self):
        """Main execution method"""
        print(f"Communications Agent starting at {datetime.now()}")

        processed_count = self.process_communication_tasks()

        print(f"Communications Agent completed - processed {processed_count} tasks")

        # Run approval manager to handle the newly created drafts
        self.approval_manager.run()

if __name__ == "__main__":
    agent = CommunicationsAgent()
    agent.run()