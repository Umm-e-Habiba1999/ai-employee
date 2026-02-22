#!/usr/bin/env python3
"""
Finance Agent
Reads bank transactions, categorizes expenses, flags subscription issues, NEVER auto-pay
"""

import os
import json
from datetime import datetime
from pathlib import Path

class FinanceAgent:
    def __init__(self, vault_path="./vault", skills_dir="./skills", ai_client=None):
        self.vault_path = Path(vault_path)
        self.skills_dir = Path(skills_dir)
        self.ai_client = ai_client  # OpenRouter AI client
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.accounting_dir = self.vault_path / "Accounting"
        self.plans_dir = self.vault_path / "Plans"

        # Import skills
        import sys
        sys.path.append(str(self.skills_dir))

        from approval_manager import ApprovalManager
        from audit_logger import AuditLogger

        self.approval_manager = ApprovalManager(vault_path)
        self.audit_logger = AuditLogger(vault_path)

    def monitor_finance_tasks(self):
        """Monitor for new finance-related tasks in Needs_Action"""
        finance_keywords = ['finance', 'payment', 'expense', 'bill', 'transaction', 'bank', 'subscription', 'money', 'cost', 'budget']

        finance_tasks = []
        for item in self.needs_action_dir.glob("*.md"):
            content = item.read_text().lower()
            if any(keyword in content for keyword in finance_keywords):
                finance_tasks.append(item)

        return finance_tasks

    def categorize_expense(self, description):
        """Categorize an expense based on description"""
        categories = {
            'utilities': ['electricity', 'gas', 'water', 'internet', 'phone', 'utilities'],
            'subscriptions': ['subscription', 'netflix', 'spotify', 'amazon', 'prime', 'membership', 'recurring'],
            'food': ['grocery', 'restaurant', 'food', 'delivery', 'meal'],
            'transportation': ['gas', 'fuel', 'transport', 'car', 'uber', 'taxi'],
            'entertainment': ['movie', 'game', 'entertainment', 'theater', 'event'],
            'health': ['pharmacy', 'doctor', 'health', 'medical', 'insurance'],
            'business': ['office', 'software', 'business', 'work', 'professional'],
        }

        description_lower = description.lower()
        for category, keywords in categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category

        return 'other'

    def analyze_transaction(self, task_file):
        """Analyze a financial transaction task"""
        content = task_file.read_text()

        # Extract transaction details (simplified parsing)
        lines = content.split('\n')
        transaction_info = {
            'amount': 'Unknown',
            'description': 'Unknown',
            'date': datetime.now().isoformat(),
            'original_task': task_file.stem
        }

        # Look for common patterns in the content
        for line in lines:
            line_lower = line.lower()
            if '$' in line:
                # Extract amount (simplified)
                import re
                amounts = re.findall(r'\$?([0-9,]+\.?[0-9]*)', line)
                if amounts:
                    transaction_info['amount'] = amounts[0]
            if 'for ' in line_lower or 'on ' in line_lower:
                transaction_info['description'] = line.strip()

        # Categorize the transaction
        category = self.categorize_expense(transaction_info['description'])
        transaction_info['category'] = category

        return transaction_info

    def create_finance_plan(self, task_file, transaction_info):
        """Create a finance plan that requires approval"""
        plan_content = f"""---
title: "Finance Plan for {task_file.stem}"
created: {datetime.now().isoformat()}
original_task: {task_file.stem}
transaction_id: {task_file.stem}
amount: {transaction_info['amount']}
category: {transaction_info['category']}
action_required: review_and_approve
status: pending_approval
---

# Finance Plan: {task_file.stem}

## Transaction Details
- **Amount**: ${transaction_info['amount']}
- **Description**: {transaction_info['description']}
- **Category**: {transaction_info['category']}
- **Date**: {transaction_info['date']}

## Recommended Action
Based on category ({transaction_info['category']}), this transaction requires human approval.

## Approval Required
- [ ] Approve transaction
- [ ] Modify amount/description
- [ ] Reject transaction
- [ ] Flag for review

## Category Notes
Category: {transaction_info['category']}
- **Subscriptions**: Monitor for renewals, potential cancellations
- **Utilities**: Expected recurring expense
- **Business**: Valid business expense

## Financial Impact
- Budget impact: ${transaction_info['amount']}
- Monthly spending in category: [Calculated if tracking]
- Annual cost if recurring: [Calculated if subscription]

## Security Considerations
- This transaction requires explicit approval
- No auto-payment functionality enabled
- All financial actions logged

## Next Steps
1. Review transaction details
2. Approve or reject in Pending_Approval directory
3. Transaction will NOT proceed without approval
"""

        # Save plan to Plans directory
        plan_path = self.plans_dir / f"finance_plan_{task_file.stem}.md"
        plan_path.write_text(plan_content)

        # Save to accounting for record keeping
        accounting_path = self.accounting_dir / f"transaction_{task_file.stem}.md"
        accounting_path.write_text(f"""---
title: "Accounting Record: {task_file.stem}"
date: {datetime.now().isoformat()}
category: {transaction_info['category']}
amount: ${transaction_info['amount']}
status: pending_approval
---

# Accounting Record

## Transaction: {task_file.stem}
- Amount: {transaction_info['amount']}
- Category: {transaction_info['category']}
- Description: {transaction_info['description']}
- Date: {transaction_info['date']}

## Approval Status
- Status: PENDING
- Requires explicit approval before processing
""")

        self.audit_logger.log_action(
            "FINANCE_PLAN_CREATED",
            f"Created finance plan for {task_file.stem}",
            {
                "task_id": task_file.stem,
                "amount": transaction_info['amount'],
                "category": transaction_info['category']
            }
        )

        return plan_path

    def flag_subscription_issues(self):
        """Identify potential subscription issues"""
        # Look for recurring payments that might be problematic
        accounting_files = list(self.accounting_dir.glob("transaction_*.md"))

        subscriptions = []
        for acc_file in accounting_files:
            content = acc_file.read_text()
            if any(word in content.lower() for word in ['subscription', 'recurring', 'monthly']):
                subscriptions.append(acc_file)

        # Flag potential issues
        flagged_issues = []
        for sub_file in subscriptions:
            content = sub_file.read_text()
            if 'cancelled' not in content.lower() and 'stopped' not in content.lower():
                flagged_issues.append({
                    'file': sub_file.name,
                    'description': 'Active subscription requiring monitoring'
                })

        if flagged_issues:
            self.create_subscription_monitoring_plan(flagged_issues)

    def create_subscription_monitoring_plan(self, flagged_issues):
        """Create a plan to monitor subscription issues"""
        plan_content = f"""---
title: "Subscription Monitoring Plan"
created: {datetime.now().isoformat()}
type: subscription_monitoring
status: active
---

# Subscription Monitoring Plan

## Flagged Subscriptions
"""
        for issue in flagged_issues:
            plan_content += f"- {issue['file']}: {issue['description']}\n"

        plan_content += f"""
## Monitoring Actions Required
- Review each subscription for necessity
- Consider cancellation of unused subscriptions
- Track monthly costs

## Next Review
This monitoring plan will be reviewed weekly for new subscription issues.
"""

        plan_path = self.plans_dir / f"subscription_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        plan_path.write_text(plan_content)

    def process_finance_tasks(self):
        """Process all finance-related tasks"""
        finance_tasks = self.monitor_finance_tasks()

        processed_count = 0
        for task in finance_tasks:
            print(f"Processing finance task: {task.name}")

            try:
                transaction_info = self.analyze_transaction(task)
                plan_path = self.create_finance_plan(task, transaction_info)
                print(f"Created finance plan: {plan_path.name}")

                # Move original task to avoid re-processing
                done_dir = self.vault_path / "Done"
                done_dir.mkdir(parents=True, exist_ok=True)
                completed_path = done_dir / f"processed_finance_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task.name}"
                task.rename(completed_path)

                processed_count += 1
            except Exception as e:
                self.audit_logger.log_error(
                    "FINANCE_PROCESSING_ERROR",
                    f"Error processing {task.name}: {str(e)}",
                    {"task_file": task.name}
                )

        return processed_count

    def run(self):
        """Main execution method"""
        print(f"Finance Agent starting at {datetime.now()}")

        processed_count = self.process_finance_tasks()
        self.flag_subscription_issues()

        print(f"Finance Agent completed - processed {processed_count} tasks")

        # Run approval manager to handle the newly created finance plans
        self.approval_manager.run()

if __name__ == "__main__":
    agent = FinanceAgent()
    agent.run()