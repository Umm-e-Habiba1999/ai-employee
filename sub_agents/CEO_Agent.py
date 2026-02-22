#!/usr/bin/env python3
"""
CEO Agent
Generates weekly strategic briefing, suggests cost optimization
"""

import os
import json
from datetime import datetime, date
from pathlib import Path

class CEOStrategicAgent:
    def __init__(self, vault_path="./vault", skills_dir="./skills", ai_client=None):
        self.vault_path = Path(vault_path)
        self.skills_dir = Path(skills_dir)
        self.ai_client = ai_client  # OpenRouter AI client
        self.business_goals_path = self.vault_path / "Business_Goals.md"
        self.accounting_dir = self.vault_path / "Accounting"
        self.done_dir = self.vault_path / "Done"
        self.briefings_dir = self.vault_path / "Briefings"
        self.plans_dir = self.vault_path / "Plans"

        # Import skills
        import sys
        sys.path.append(str(self.skills_dir))

        from weekly_ceo_briefing import WeeklyCEOBriefing
        from audit_logger import AuditLogger
        from dashboard_updater import DashboardUpdater

        self.briefing_generator = WeeklyCEOBriefing(vault_path)
        self.audit_logger = AuditLogger(vault_path)
        self.dashboard_updater = DashboardUpdater(vault_path)

    def analyze_business_performance(self):
        """Analyze business performance based on goals and completed tasks"""
        # Read business goals
        if self.business_goals_path.exists():
            goals_content = self.business_goals_path.read_text()
        else:
            goals_content = "No business goals defined"

        # Count completed tasks
        import glob
        done_files = list(self.done_dir.glob("*.md"))
        completed_count = len(done_files)

        # Analyze accounting data
        accounting_files = list(self.accounting_dir.glob("*.md"))
        cost_savings_identified = len(accounting_files)  # Placeholder for real analysis

        performance_data = {
            'goals_status': goals_content[:500],  # First 500 chars as summary
            'completed_tasks_count': completed_count,
            'cost_savings_identified': cost_savings_identified,
            'last_analysis': datetime.now().isoformat()
        }

        return performance_data

    def identify_cost_optimization_opportunities(self):
        """Identify potential cost optimization opportunities"""
        opportunities = []

        # Look through accounting records for potential savings
        for acc_file in self.accounting_dir.glob("*.md"):
            content = acc_file.read_text().lower()

            # Look for subscription-like expenses
            if any(word in content for word in ['subscription', 'monthly', 'recurring', 'annual']):
                opportunities.append({
                    'type': 'subscription_review',
                    'file': acc_file.name,
                    'description': f'Review {acc_file.name} for potential cancellation or optimization'
                })

            # Look for high-value expenses
            import re
            amounts = re.findall(r'\$([0-9,]+\.?[0-9]*)', content)
            for amount_str in amounts:
                try:
                    amount = float(amount_str.replace(',', ''))
                    if amount > 100:  # Threshold for "high value"
                        opportunities.append({
                            'type': 'high_value_expense',
                            'file': acc_file.name,
                            'amount': amount,
                            'description': f'High-value expense of ${amount} in {acc_file.name}'
                        })
                except ValueError:
                    continue

        return opportunities

    def create_strategic_plan(self):
        """Create a strategic plan based on analysis"""
        performance_data = self.analyze_business_performance()
        cost_opportunities = self.identify_cost_optimization_opportunities()

        strategic_content = f"""---
title: "Strategic Analysis and Plan"
created: {datetime.now().isoformat()}
analysis_type: strategic
status: generated
---

# Strategic Analysis & Plan

## Business Performance Overview
- **Goals Status**: {performance_data['goals_status'][:200]}...
- **Tasks Completed**: {performance_data['completed_tasks_count']}
- **Cost Savings Identified**: {performance_data['cost_savings_identified']}
- **Last Analysis**: {performance_data['last_analysis']}

## Strategic Insights

### Productivity Metrics
- Auto-processing: {performance_data['completed_tasks_count']} tasks completed
- Goal alignment: [Based on business goals content]
- Efficiency gains: [Estimated based on time saved]

### Financial Insights
- Recurring costs: [Analyzed from accounting records]
- One-time expenses: [Analyzed from accounting records]
- Potential savings: {len(cost_opportunities)} opportunities identified

## Cost Optimization Opportunities
"""
        for i, opp in enumerate(cost_opportunities, 1):
            strategic_content += f"""
### Opportunity {i}: {opp['type'].title()}
- **Item**: {opp['file']}
- **Description**: {opp['description']}
- **Potential Impact**: [Estimated savings]
"""

        strategic_content += f"""
## Strategic Recommendations

### Short-term (1-4 weeks)
1. Implement identified cost optimizations
2. Review high-priority business goals alignment
3. Optimize task processing workflows

### Medium-term (1-3 months)
1. Expand automation to new task categories
2. Enhance financial monitoring capabilities
3. Improve reporting and analytics

### Long-term (3-12 months)
1. Achieve Silver tier autonomy
2. Implement predictive analytics
3. Develop advanced optimization algorithms

## Next Strategic Steps
1. Review and approve strategic recommendations
2. Implement top-priority cost optimizations
3. Update business goals based on performance
4. Schedule next strategic review

## Monitoring Requirements
- Weekly performance reviews
- Monthly cost optimization checks
- Quarterly goal alignment assessments
"""

        # Save strategic plan
        strategic_path = self.plans_dir / f"strategic_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        strategic_path.write_text(strategic_content)

        self.audit_logger.log_action(
            "STRATEGIC_PLAN_CREATED",
            "Created strategic analysis and plan",
            {
                "completed_tasks": performance_data['completed_tasks_count'],
                "optimization_opportunities": len(cost_opportunities)
            }
        )

        return strategic_path

    def generate_weekly_briefing(self):
        """Generate the weekly CEO briefing"""
        # Use the existing briefing generator skill
        briefing_path = self.briefing_generator.generate_briefing()
        return briefing_path

    def run(self):
        """Main execution method"""
        print(f"CEO Strategic Agent starting at {datetime.now()}")

        # Create strategic analysis
        strategic_plan_path = self.create_strategic_plan()
        print(f"Created strategic plan: {strategic_plan_path.name}")

        # Generate weekly briefing
        briefing_path = self.generate_weekly_briefing()
        print(f"Generated weekly briefing: {briefing_path.name}")

        # Update dashboard to reflect CEO activities
        self.dashboard_updater.run("CEO Agent strategic review")

        print("CEO Strategic Agent completed")

if __name__ == "__main__":
    agent = CEOStrategicAgent()
    agent.run()