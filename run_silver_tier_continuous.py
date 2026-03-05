#!/usr/bin/env python3
"""
Continuous Silver Tier Coordinator
Watches incoming folder, processes tasks, and handles approvals
"""
from silver_tier_coordinator import SilverTierCoordinator
import time
import signal
import sys

def signal_handler(sig, frame):
    print('\nShutting down Silver Tier Coordinator...')
    sys.exit(0)

# Register signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print("Starting Silver Tier Coordinator in continuous mode...")
print("Press Ctrl+C to stop")

# Create Silver Tier Coordinator instance
coordinator = SilverTierCoordinator()

# Start the file watcher
coordinator.file_watcher.start()
print("File watcher started, monitoring incoming/ folder")

try:
    # Main processing loop
    while True:
        # Process any new tasks in Needs_Action and generate plans
        coordinator.planning_layer.process_needs_action_tasks()

        # Process approval workflow
        coordinator.human_in_loop.process_approval_workflow()

        # Update dashboard with current counts
        coordinator.update_dashboard()

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Silver Tier cycle completed, sleeping for 60 seconds...")

        # Sleep for 60 seconds before next cycle
        time.sleep(60)

except KeyboardInterrupt:
    print('\nKeyboard interrupt received, shutting down Silver Tier Coordinator...')
except Exception as e:
    print(f"Error in Silver Tier Coordinator: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Stop the file watcher when exiting
    coordinator.file_watcher.stop()
    print("Silver Tier Coordinator stopped.")