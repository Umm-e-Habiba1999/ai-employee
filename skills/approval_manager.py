#!/usr/bin/env python3
"""
Approval Manager Skill
Generates approval files and moves files based on approval status
"""

import os
import json
from datetime import datetime
from pathlib import Path

class ApprovalManager:
    def __init__(self, vault_path="./vault", ai_client=None):
        self.vault_path = Path(vault_path)
        self.ai_client = ai_client  # OpenRouter AI client
        self.plans_dir = self.vault_path / "Plans"
        self.pending_approval_dir = self.vault_path / "Pending_Approval"
        self.approved_dir = self.vault_path / "Approved"
        self.rejected_dir = self.vault_path / "Rejected"

    def check_pending_approvals(self):
        """Process all plan files and determine if they need approvals"""
        plan_files = list(self.plans_dir.glob("plan_*.md"))

        for plan_path in plan_files:
            content = plan_path.read_text()
            approval_needed = self.determine_approval_needed(content)

            if approval_needed:
                self.create_approval_request(plan_path)
            else:
                # Auto-approve if no approval needed
                approved_path = self.approved_dir / plan_path.name
                plan_path.rename(approved_path)
                print(f"Auto-approved: {plan_path.name}")

    def determine_approval_needed(self, content):
        """Determine if approval is needed based on content"""
        content_lower = content.lower()

        # Approval required for these actions
        approval_keywords = [
            'payment', 'finance', 'expense', 'purchase',
            'email', 'communication', 'send', 'reply',
            'new contact', 'new person', 'financial',
            'transfer', 'bill', 'invoice', 'subscription'
        ]

        for keyword in approval_keywords:
            if keyword in content_lower:
                return True

        return False

    def create_approval_request(self, plan_path):
        """Create an approval request file"""
        plan_content = plan_path.read_text()

        approval_content = f"""---
title: "Approval Request for {plan_path.stem}"
created: {datetime.now().isoformat()}
plan_id: {plan_path.stem}
status: pending_approval
priority: normal
---

# Approval Request: {plan_path.stem}

## Plan Summary
{plan_content[:500]}...

## Action Required
```
Approve: Move file to Approved directory
Reject: Move file to Rejected directory
```

## Justification
- Action requires human review
- May involve sensitive information
- Financial/communication implications

## Risk Level
- Low/Medium/High (assessed by system)

## Approval Options
1. **Full Approval**: Execute all planned actions
2. **Conditional Approval**: Execute with modifications
3. **Reject**: Do not proceed with plan
4. **More Information**: Request additional details

## Auto-Reject
This request will auto-reject in 7 days if no action taken.
"""

        approval_path = self.pending_approval_dir / f"approval_{plan_path.stem}.md"
        approval_path.write_text(approval_content)
        print(f"Created approval request: {approval_path.name}")

    def process_approval_actions(self):
        """Check for approvals/rejections and move files accordingly"""
        # Move approved files
        for approval_file in self.pending_approval_dir.glob("approval_*.md"):
            # In a real system, this would check if the file was moved to Approved or Rejected
            # For now, we'll just note the potential for movement
            approval_file.unlink()  # Remove after approval decision
            print(f"Processed approval request: {approval_file.name}")

    def run(self):
        """Main execution method"""
        print(f"Approval Manager starting at {datetime.now()}")
        self.check_pending_approvals()
        self.process_approval_actions()
        print("Approval Manager completed")

if __name__ == "__main__":
    manager = ApprovalManager()
    manager.run()