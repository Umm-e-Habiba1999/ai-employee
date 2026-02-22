#!/usr/bin/env python3
"""
Main AI Employee System
Coordinates all agents and skills according to Hackathon 0 documentation
"""

import os
import sys
import time
import signal
from datetime import datetime
from pathlib import Path

# Add skills, sub_agents and utils to path
sys.path.append("./skills")
sys.path.append("./sub_agents")
sys.path.append("./utils")

# Import OpenRouter client
from utils.openrouter_client import OpenRouterClient

class AIEmployeeSystem:
    def __init__(self, vault_path="./vault"):
        self.vault_path = Path(vault_path)
        self.running = False

        # Initialize OpenRouter client
        self.ai_client = OpenRouterClient()

        # Import agents and skills
        from skills.inbox_processor import InboxProcessor
        from skills.approval_manager import ApprovalManager
        from skills.dashboard_updater import DashboardUpdater
        from skills.audit_logger import AuditLogger
        from skills.task_completion_checker import TaskCompletionChecker
        from sub_agents.Communications_Agent import CommunicationsAgent
        from sub_agents.Finance_Agent import FinanceAgent
        from sub_agents.Operations_Agent import OperationsAgent
        from sub_agents.CEO_Agent import CEOStrategicAgent

        # Initialize components
        self.inbox_processor = InboxProcessor(vault_path)
        self.approval_manager = ApprovalManager(vault_path)
        self.dashboard_updater = DashboardUpdater(vault_path)
        self.audit_logger = AuditLogger(vault_path)
        self.task_completion_checker = TaskCompletionChecker(vault_path)

        # Pass vault_path and ai_client to agents
        self.communications_agent = CommunicationsAgent(vault_path, ai_client=self.ai_client)
        self.finance_agent = FinanceAgent(vault_path, ai_client=self.ai_client)
        self.operations_agent = OperationsAgent(vault_path, ai_client=self.ai_client)
        self.ceo_agent = CEOStrategicAgent(vault_path, ai_client=self.ai_client)

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        self.running = False

    def process_needs_action(self):
        """Process items in Needs_Action directory"""
        print(f"[{datetime.now()}] Processing Needs_Action items...")

        # Run inbox processor to classify and plan tasks
        self.inbox_processor.run()

        # Run approval manager to handle new plans
        self.approval_manager.run()

    def run_agents(self):
        """Run all specialized agents"""
        print(f"[{datetime.now()}] Running specialized agents...")

        try:
            # Run communications agent
            self.communications_agent.run()
        except Exception as e:
            print(f"Error running Communications Agent: {e}")

        try:
            # Run finance agent
            self.finance_agent.run()
        except Exception as e:
            print(f"Error running Finance Agent: {e}")

        try:
            # Run operations agent
            self.operations_agent.run()
        except Exception as e:
            print(f"Error running Operations Agent: {e}")

        try:
            # Run CEO agent (strategic analysis)
            self.ceo_agent.run()
        except Exception as e:
            print(f"Error running CEO Agent: {e}")

    def maintenance_tasks(self):
        """Run maintenance tasks"""
        print(f"[{datetime.now()}] Running maintenance tasks...")

        # Check for completed tasks and move to Done
        self.task_completion_checker.run()

        # Update dashboard with AI client status
        mode = "LIVE" if not self.ai_client.dry_run and self.ai_client.api_key else "DRY_RUN"
        connected_services = self.ai_client.get_client_info()

        # Update dashboard
        self.dashboard_updater.run("System maintenance cycle", ai_mode=mode, connected_services=connected_services)

        # Log system status
        self.audit_logger.log_action(
            "SYSTEM_MAINTENANCE",
            "Completed maintenance cycle",
            {
                "cycle_time": datetime.now().isoformat(),
                "components_active": 8,  # Total components
                "ai_mode": mode,
                "connected_services": connected_services
            }
        )

    def run_single_cycle(self):
        """Run one complete cycle of the AI Employee system"""
        print(f"\n[{datetime.now()}] Starting AI Employee cycle...")

        try:
            # Process any new items in Needs_Action
            self.process_needs_action()

            # Run specialized agents
            self.run_agents()

            # Run maintenance tasks
            self.maintenance_tasks()

            print(f"[{datetime.now()}] AI Employee cycle completed successfully")

        except Exception as e:
            print(f"Error in cycle: {e}")
            self.audit_logger.log_error("CYCLE_ERROR", str(e), {"cycle_time": datetime.now().isoformat()})

    def run_continuous(self, cycle_interval=300):  # Default 5 minutes
        """Run the system continuously with specified interval between cycles"""
        print(f"Starting AI Employee system in continuous mode (cycle interval: {cycle_interval}s)")
        self.audit_logger.log_action("SYSTEM_START", "AI Employee system started in continuous mode", {
            "cycle_interval": cycle_interval,
            "start_time": datetime.now().isoformat()
        })

        self.running = True

        while self.running:
            try:
                self.run_single_cycle()
                print(f"Waiting {cycle_interval} seconds until next cycle...")
                time.sleep(cycle_interval)
            except KeyboardInterrupt:
                print("\nKeyboard interrupt received, shutting down...")
                break

        print("AI Employee system shutting down...")
        self.audit_logger.log_action("SYSTEM_STOP", "AI Employee system stopped", {
            "stop_time": datetime.now().isoformat()
        })

    def run_once(self):
        """Run the system once and exit"""
        print("Starting AI Employee system in single-run mode")
        self.audit_logger.log_action("SYSTEM_START", "AI Employee system started in single-run mode", {
            "start_time": datetime.now().isoformat()
        })

        self.run_single_cycle()

        self.audit_logger.log_action("SYSTEM_STOP", "AI Employee system stopped after single run", {
            "stop_time": datetime.now().isoformat()
        })

def main():
    import argparse

    parser = argparse.ArgumentParser(description="AI Employee System")
    parser.add_argument("--mode", choices=["once", "continuous"], default="once",
                       help="Run mode: once (single cycle) or continuous (loop)")
    parser.add_argument("--interval", type=int, default=300,
                       help="Cycle interval in seconds (for continuous mode)")
    parser.add_argument("--vault", default="./vault",
                       help="Path to vault directory")

    args = parser.parse_args()

    system = AIEmployeeSystem(vault_path=args.vault)

    if args.mode == "continuous":
        system.run_continuous(cycle_interval=args.interval)
    else:
        system.run_once()

if __name__ == "__main__":
    main()