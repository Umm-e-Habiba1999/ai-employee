# AI Employee System

Welcome to your Personal AI Employee - an autonomous, local-first, agent-driven system designed to handle routine tasks while maintaining human-in-the-loop oversight for critical decisions.

## Architecture Overview

The system follows the Hackathon 0 architecture with Bronze Tier foundation, designed for scalability to Silver and Gold tiers.

### Core Components

#### Perception Layer
- **Gmail Watcher** (Python): Monitors email for tasks
- **WhatsApp Watcher** (Playwright): Monitors WhatsApp messages
- **FileSystem Watcher**: Monitors file system changes
- **Finance Watcher**: Monitors financial transactions

#### AI Reasoning Layer
- **OpenRouter Client**: Connects to Claude via OpenRouter API (anthropic/claude-3-haiku)
- **Claude Code**: Reads vault and creates Plan.md files
- **Plan Generation**: Creates structured action plans
- **Approval Processing**: Generates approval requirements when needed

#### Action Layer
- **MCP Servers**: Execute approved actions
- **Human-in-the-Loop**: Critical decisions require explicit approval
- **Never Act Directly**: Without proper authorization for sensitive operations

#### Persistence Layer
- **Ralph Wiggum Loop Compatibility**: Ensures continuous operation
- **Task Completion**: Only when files moved to `/Done` directory

### Directory Structure
```
vault/
├── Needs_Action/           # New tasks to be processed
├── Plans/                  # Generated action plans
├── Done/                   # Completed tasks
├── Logs/                   # System logs and audit trails
├── Pending_Approval/       # Tasks awaiting human approval
├── Approved/               # Approved tasks
├── Rejected/               # Rejected tasks
├── Accounting/             # Financial records
├── Briefings/              # Generated reports
├── Active_Projects/        # Active project tracking
├── Skills/                 # Skill-related documents
├── Sub_Agents/             # Sub-agent documentation
├── Dashboard.md            # Main system dashboard
├── Company_Handbook.md     # Operational guidelines
└── Business_Goals.md       # Strategic objectives
```

## Core Skills

### 1. Inbox Processor (`skills/inbox_processor.py`)
- Reads `/Needs_Action` and classifies items
- Creates Plan files with appropriate categorization
- Assigns tasks to relevant sub-agents

### 2. Approval Manager (`skills/approval_manager.py`)
- Generates approval files for sensitive operations
- Manages approval workflow
- Moves files based on approval status

### 3. Dashboard Updater (`skills/dashboard_updater.py`)
- Updates `Dashboard.md` with current system status
- Tracks metrics and recent activity
- Maintains system visibility

### 4. Audit Logger (`skills/audit_logger.py`)
- Writes structured logs to `/Logs/YYYY-MM-DD.json`
- Maintains security and compliance records
- Tracks all system actions

### 5. Weekly CEO Briefing (`skills/weekly_ceo_briefing.py`)
- Generates strategic briefings
- Analyzes completed work against business goals
- Provides actionable insights

### 6. Task Completion Checker (`skills/task_completion_checker.py`)
- Verifies task completion status
- Moves files to `/Done` when complete
- Maintains workflow integrity

## Sub-Agents

### 1. Communications Agent (`sub_agents/Communications_Agent.py`)
- Handles Gmail and WhatsApp interactions
- Drafts replies for approval
- Never sends without explicit approval

### 2. Finance Agent (`sub_agents/Finance_Agent.py`)
- Processes financial transactions
- Categorizes expenses
- Flags subscription issues
- Never auto-pays without approval

### 3. Operations Agent (`sub_agents/Operations_Agent.py`)
- Manages projects and deadlines
- Tracks milestones and deliverables
- Identifies operational bottlenecks

### 4. CEO Agent (`sub_agents/CEO_Agent.py`)
- Generates strategic briefings
- Analyzes cost optimization opportunities
- Provides high-level oversight

## Security Requirements

1. No credentials stored in vault
2. Use `.env` for secrets
3. DRY_RUN mode as default (true)
4. All payments require approval
5. New contacts require approval
6. All actions logged for audit trail

## Getting Started

1. **Setup**:
   ```bash
   git clone <your-repo>
   cd ai-employee
   cp .env.example .env
   # Edit .env with your OpenRouter API key and other credentials
   ```

2. **Configure AI Client**:
   - Set `OPENROUTER_API_KEY` in your `.env` file (replaces CLAUDE_API_KEY)
   - Set `DRY_RUN=false` to enable live API mode
   - Dashboard will show "Mode: LIVE" and "Connected Services: Claude (OpenRouter)" when connected

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the System**:
   ```bash
   # Single run mode
   python main.py --mode once

   # Continuous mode (runs every 5 minutes by default)
   python main.py --mode continuous
   ```

5. **Add Tasks**:
   - Place new tasks in the `vault/Needs_Action/` directory
   - The system will automatically process them in the next cycle

## Work Mode

The system follows this iterative process for each task:

1. Read vault for new items in `/Needs_Action`
2. Think and analyze the request
3. Create `Plan.md` with proposed actions
4. Execute via appropriate Skills
5. Request approval if required by security policies
6. Log all actions for audit trail
7. Move completed tasks to `/Done` directory

## Bronze Tier Features

✅ Full Human-in-the-Loop oversight
✅ Task automation with approval requirements
✅ Financial oversight with approval gates
✅ Communication handling with approval
✅ Project management and tracking
✅ Audit logging and compliance
✅ Dashboard monitoring
✅ Strategic reporting

## Roadmap to Silver & Gold Tiers

**Silver Tier**:
- Select autonomous operations with periodic check-ins
- Advanced decision-making capabilities
- Enhanced integration with external services

**Gold Tier**:
- Advanced autonomous operations with strategic oversight
- Predictive analytics and proactive suggestions
- Multi-agent coordination and optimization

## Contributing

This system is designed to be modular and extensible. When adding new features:
- Create new Skills following the established patterns
- Build Sub-Agents that leverage existing Skills
- Maintain security and approval requirements
- Follow the established file structure and naming conventions

## Support

For issues or questions:
1. Check the logs in `vault/Logs/`
2. Review `Company_Handbook.md` for operational guidelines
3. Ensure all security requirements are properly configured