#!/usr/bin/env python3
"""
LinkedIn Watcher Module for AI Employee System
Automatically monitors tasks that are approved in the Silver Tier system and posts to LinkedIn.
"""
import os
import json
import time
import traceback
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.linkedin_poster import LinkedInPoster

class LinkedInWatcher:
    """
    LinkedIn automation class that monitors for approved tasks and automatically posts to LinkedIn
    """
    def __init__(self, vault_path: str = "./vault", logs_path: str = "./logs", check_interval: int = 30):
        self.vault_path = Path(vault_path)
        self.approved_path = self.vault_path / "Approved"
        self.logs_path = Path(logs_path)
        self.check_interval = check_interval  # seconds between checks
        self.running = False
        self.last_check_time = None

        # Ensure directories exist
        self.logs_path.mkdir(exist_ok=True)
        self.approved_path.mkdir(exist_ok=True)

        # Setup logging
        log_file = self.logs_path / "linkedin_watcher.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Initialize LinkedIn poster
        try:
            self.linkedin_poster = LinkedInPoster(self.logs_path)
            self.logger.info("LinkedIn poster initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize LinkedIn poster: {str(e)}")
            raise

        # Track processed files to avoid duplicates
        self.processed_files = set()
        self.load_processed_files()

    def load_processed_files(self):
        """Load list of already processed files to avoid re-processing"""
        processed_log = self.logs_path / "linkedin_watcher_processed.json"
        if processed_log.exists():
            try:
                with open(processed_log, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_files = set(data.get('processed_files', []))
            except Exception as e:
                self.logger.error(f"Error loading processed files: {str(e)}")
                self.processed_files = set()

    def save_processed_files(self):
        """Save list of processed files"""
        processed_log = self.logs_path / "linkedin_watcher_processed.json"
        try:
            with open(processed_log, 'w', encoding='utf-8') as f:
                json.dump({'processed_files': list(self.processed_files)}, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving processed files: {str(e)}")

    def start_watching(self):
        """Start watching for new approved tasks in a separate thread"""
        if self.running:
            self.logger.warning("LinkedIn Watcher is already running")
            return

        self.running = True
        self.last_check_time = datetime.now()
        self.logger.info("Starting LinkedIn Watcher...")

        # Start the monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_approved_tasks, daemon=True)
        self.monitor_thread.start()
        self.logger.info(f"LinkedIn Watcher started, checking every {self.check_interval} seconds")

    def stop_watching(self):
        """Stop watching for new approved tasks"""
        if not self.running:
            self.logger.warning("LinkedIn Watcher is not running")
            return

        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)  # Wait up to 5 seconds for thread to finish
        self.logger.info("LinkedIn Watcher stopped")

    def _monitor_approved_tasks(self):
        """Internal method to monitor the Approved folder for new tasks"""
        self.logger.info("Monitoring for approved tasks...")

        while self.running:
            try:
                # Look for new approved tasks
                self._check_approved_tasks()

                # Sleep for the specified interval
                time.sleep(self.check_interval)

            except Exception as e:
                self.logger.error(f"Error in monitor loop: {str(e)}")
                time.sleep(self.check_interval)  # Continue monitoring even if error occurs

    def _check_approved_tasks(self):
        """Check the Approved folder for new tasks to process"""
        try:
            # Get all approved files created since last check
            approved_files = list(self.approved_path.glob("*.md"))
            self.logger.info(f"Found {len(approved_files)} files in Approved folder")
            self.logger.info(f"Already processed files count: {len(self.processed_files)}")

            for approved_file in approved_files:
                self.logger.info(f"Found approved file: {approved_file.name}")
                if approved_file.name not in self.processed_files:
                    self.logger.info(f"Processing new approved task: {approved_file.name}")
                    self.process_task_file(approved_file)
                else:
                    self.logger.debug(f"Skipping already processed file: {approved_file.name}")

        except Exception as e:
            self.logger.error(f"Error checking approved tasks: {str(e)}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")

    def process_task_file(self, approved_file: Path):
        """Process an individual approved task file"""
        try:
            self.logger.info(f"Starting processing of approved task: {approved_file.name}")
            self.logger.info(f"File size: {approved_file.stat().st_size} bytes")
            self.logger.info(f"File created: {datetime.fromtimestamp(approved_file.stat().st_ctime)}")

            # Extract task information from the approved file
            task_data = self._extract_task_data(approved_file)
            self.logger.info(f"Extracted task data for: {task_data.get('title', 'Unknown Task')}")
            self.logger.info(f"Task description preview: {task_data.get('description', '')[:100]}...")

            # Process the task
            success = self.process_task(task_data)
            self.logger.info(f"Task processing result for {approved_file.name}: {'SUCCESS' if success else 'FAILED'}")

            if success:
                # Mark as processed to avoid re-processing
                self.processed_files.add(approved_file.name)
                self.save_processed_files()
                self.logger.info(f"Successfully processed and posted to LinkedIn: {approved_file.name}")

                # Move the file to Done after successful posting
                self._move_to_done(approved_file)
                self.logger.info(f"Moved successfully processed file to Done: {approved_file.name}")
            else:
                # Don't move the file to Done if posting failed, keep it in Approved for manual review
                self.logger.error(f"Failed to post to LinkedIn for task: {approved_file.name}")
                # Optionally, we can move failed files to a special folder for manual review
                self._move_to_failed(approved_file)

        except Exception as e:
            self.logger.error(f"Error processing task file {approved_file.name}: {str(e)}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")

            # Move to failed folder in case of exception to prevent repeated failures
            self._move_to_failed(approved_file)

    def _move_to_failed(self, approved_file: Path):
        """Move the approved file to the Failed folder when LinkedIn posting fails"""
        try:
            from datetime import datetime
            import shutil
            from pathlib import Path

            # Create Failed directory if it doesn't exist
            failed_path = self.vault_path / "Failed"
            failed_path.mkdir(exist_ok=True)

            # Create a unique filename in the Failed folder to prevent overwrites
            base_name = approved_file.stem
            suffix = approved_file.suffix
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            final_path = failed_path / f"failed_{timestamp}_{base_name}{suffix}"

            # Move the approved file to Failed folder for manual review
            shutil.move(str(approved_file), str(final_path))

            self.logger.info(f"Moved failed task to Failed folder: {final_path.name}")

        except Exception as e:
            self.logger.error(f"Error moving file to Failed: {str(e)}")

    def _move_to_done(self, approved_file: Path):
        """Move the approved file to the Done folder after successful processing"""
        try:
            from datetime import datetime
            import shutil
            from pathlib import Path

            # Create Done directory if it doesn't exist
            done_path = self.vault_path / "Done"
            done_path.mkdir(exist_ok=True)

            # Create a unique filename in the Done folder to prevent overwrites
            base_name = approved_file.stem
            suffix = approved_file.suffix
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            final_path = done_path / f"completed_{timestamp}_{base_name}{suffix}"

            # Move the approved file to Done after execution
            shutil.move(str(approved_file), str(final_path))

            self.logger.info(f"Moved processed task to Done folder: {final_path.name}")

        except Exception as e:
            self.logger.error(f"Error moving file to Done: {str(e)}")

    def _extract_task_data(self, approved_file: Path) -> Dict[str, Any]:
        """Extract task data from an approved file"""
        try:
            self.logger.info(f"Extracting task data from: {approved_file.name}")
            with open(approved_file, 'r', encoding='utf-8') as f:
                content = f.read()

            self.logger.info(f"File content length: {len(content)} characters")

            # Extract task information from the file content
            task_data = {
                'title': 'AI Task Completed',
                'description': 'An automated task was completed by the AI Employee system',
                'file_name': approved_file.name,
                'file_path': str(approved_file)
            }

            # Try to extract more meaningful information from the file
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'Generated from Plan:' in line:
                    # Extract the plan name from the next part
                    plan_part = line.split('Generated from Plan:')[-1].strip()
                    task_data['title'] = f"Completed: {plan_part}"
                    self.logger.info(f"Extracted title from plan: {plan_part}")
                elif 'Plan Summary' in line and i + 1 < len(lines):
                    # Look for the next few lines to extract task details
                    for j in range(i+1, min(i+10, len(lines))):
                        if lines[j].startswith('# Objective') and j + 1 < len(lines):
                            # Extract the next line which should contain the objective
                            obj_line = lines[j+1].strip()
                            if obj_line.startswith('#'):
                                task_data['description'] = obj_line[1:].strip()
                            else:
                                task_data['description'] = obj_line
                            self.logger.info(f"Extracted description from # Objective: {task_data['description'][:50]}...")
                            break
                        elif lines[j].startswith('## Objective') and j + 1 < len(lines):
                            # Extract the next line which should contain the objective
                            obj_line = lines[j+1].strip()
                            if obj_line.startswith('#'):
                                task_data['description'] = obj_line[1:].strip()
                            else:
                                task_data['description'] = obj_line
                            self.logger.info(f"Extracted description from ## Objective: {task_data['description'][:50]}...")
                            break

            self.logger.info(f"Extracted task data: {json.dumps(task_data, indent=2)[:300]}...")
            return task_data

        except Exception as e:
            self.logger.error(f"Error extracting task data from {approved_file}: {str(e)}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")

            # Return default task data
            return {
                'title': 'AI Task Completed',
                'description': 'An automated task was completed by the AI Employee system',
                'file_name': approved_file.name,
                'file_path': str(approved_file)
            }

    def process_task(self, task_data: Dict[str, Any]) -> bool:
        """
        Process a task by posting to LinkedIn

        Args:
            task_data (dict): Task data containing title, description, etc.

        Returns:
            bool: True if post was successful, False otherwise
        """
        try:
            self.logger.info(f"Processing task for LinkedIn posting: {task_data.get('title', 'Unknown Task')}")
            self.logger.info(f"Task details: {json.dumps(task_data, indent=2)[:500]}...")

            # Try to post to LinkedIn with retry logic
            max_retries = 3
            retry_count = 0

            while retry_count < max_retries:
                self.logger.info(f"Attempting LinkedIn post (attempt {retry_count + 1}/{max_retries}) for: {task_data.get('title', 'Unknown Task')}")

                try:
                    success = self.linkedin_poster.post_after_approval(task_data)
                    if success:
                        self.logger.info(f"Successfully posted to LinkedIn: {task_data.get('title', 'Unknown Task')}")
                        return True
                    else:
                        self.logger.warning(f"Failed to post to LinkedIn (attempt {retry_count + 1}): {task_data.get('title', 'Unknown Task')}")
                        retry_count += 1
                        if retry_count < max_retries:
                            self.logger.info(f"Retrying in 5 seconds... ({max_retries - retry_count} attempts remaining)")
                            time.sleep(5)  # Wait 5 seconds before retrying

                except Exception as e:
                    self.logger.error(f"Error during LinkedIn posting (attempt {retry_count + 1}): {str(e)}")
                    import traceback
                    self.logger.error(f"Full traceback: {traceback.format_exc()}")
                    retry_count += 1
                    if retry_count < max_retries:
                        self.logger.info(f"Retrying in 5 seconds... ({max_retries - retry_count} attempts remaining)")
                        time.sleep(5)  # Wait 5 seconds before retrying

            self.logger.error(f"Failed to post to LinkedIn after {max_retries} attempts: {task_data.get('title', 'Unknown Task')}")
            return False

        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return False

    def log_event(self, message: str):
        """Log event to system log file"""
        log_file = self.logs_path / "system.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] LinkedIn Watcher: {message}\n")


def main():
    """Main function to run the LinkedIn Watcher"""
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn Watcher for AI Employee System")
    parser.add_argument("--vault", default="./vault", help="Path to vault directory")
    parser.add_argument("--logs", default="./logs", help="Path to logs directory")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    parser.add_argument("--test", action="store_true", help="Test mode - process one cycle then exit")

    args = parser.parse_args()

    watcher = LinkedInWatcher(
        vault_path=args.vault,
        logs_path=args.logs,
        check_interval=args.interval
    )

    if args.test:
        # Test mode: process one cycle then exit
        print("Testing LinkedIn Watcher...")
        print(f"Vault path: {watcher.vault_path}")
        print(f"Approved path: {watcher.approved_path}")
        print(f"Logs path: {watcher.logs_path}")
        print(f"Check interval: {watcher.check_interval} seconds")

        # Process current approved tasks
        watcher._check_approved_tasks()
        print("Test cycle completed")
    else:
        # Continuous mode
        print("Starting LinkedIn Watcher in continuous mode...")
        print(f"Monitoring: {watcher.approved_path}")
        print(f"Check interval: {watcher.check_interval} seconds")

        watcher.start_watching()

        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping LinkedIn Watcher...")
            watcher.stop_watching()
            print("LinkedIn Watcher stopped")


if __name__ == "__main__":
    main()