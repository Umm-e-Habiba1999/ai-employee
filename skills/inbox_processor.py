#!/usr/bin/env python3
"""
Inbox Processor Skill
Reads /Needs_Action and classifies items, creating Plan files
"""

import os
import json
from datetime import datetime
from pathlib import Path

class InboxProcessor:
    def __init__(self, vault_path="./vault", ai_client=None):
        self.vault_path = Path(vault_path)
        self.ai_client = ai_client  # OpenRouter AI client
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.plans_dir = self.vault_path / "Plans"

    def process_inbox(self):
        """Process all items in Needs_Action directory"""
        items = list(self.needs_action_dir.glob("*.md"))

        for item_path in items:
            print(f"Processing: {item_path.name}")
            classification = self.classify_item(item_path)
            self.create_plan(item_path, classification)

    def classify_item(self, item_path):
        """Classify the item based on content"""
        content = item_path.read_text()

        # Basic classification logic
        if any(keyword in content.lower() for keyword in ['email', 'gmail', 'communication']):
            return 'COMMUNICATION'
        elif any(keyword in content.lower() for keyword in ['finance', 'payment', 'expense', 'bill']):
            return 'FINANCE'
        elif any(keyword in content.lower() for keyword in ['file', 'document', 'organize']):
            return 'FILE_MANAGEMENT'
        elif any(keyword in content.lower() for keyword in ['project', 'task', 'deadline']):
            return 'PROJECT_MANAGEMENT'
        else:
            return 'GENERAL'

    def create_plan(self, item_path, classification):
        """Create a plan file based on classification"""
        item_content = item_path.read_text()

        plan_content = f"""---
title: "Plan for {item_path.stem}"
created: {datetime.now().isoformat()}
item_id: {item_path.stem}
classification: {classification}
status: pending
---

# Plan for {item_path.stem}

## Item Summary
{item_content[:200]}...

## Classification
{classification}

## Action Steps
1. Analyze requirements
2. Check for human-in-the-loop requirements
3. Execute appropriate skill
4. Log completion
5. Move to Done folder

## Sub-Agent Assignment
- Classification: {classification}
- Assigned Agent: Auto-determined

## Approval Required
- Auto-pay: false
- Financial: depends on amount
- Communication: depends on context
- File access: depends on sensitivity

## Estimated Time
- Complexity: medium
- Duration: 15-30 minutes
"""

        plan_path = self.plans_dir / f"plan_{item_path.stem}.md"
        plan_path.write_text(plan_content)
        print(f"Created plan: {plan_path.name}")

    def run(self):
        """Main execution method"""
        print(f"Inbox Processor starting at {datetime.now()}")
        self.process_inbox()
        print("Inbox Processor completed")

if __name__ == "__main__":
    processor = InboxProcessor()
    processor.run()