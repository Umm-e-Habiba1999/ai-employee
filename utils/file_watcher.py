#!/usr/bin/env python3
"""
File Watcher Module for AI Employee System
Monitors the incoming folder and creates structured task files when new files are added.
"""
import os
import time
import json
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

class FileWatcherHandler(FileSystemEventHandler):
    """Custom event handler for file system events"""

    def __init__(self, incoming_path, vault_path):
        self.incoming_path = Path(incoming_path)
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.logs_path = Path("logs")

        # Create logs directory if it doesn't exist
        self.logs_path.mkdir(exist_ok=True)

        # Set up logging
        self.setup_logging()

    def setup_logging(self):
        """Set up logging for the file watcher"""
        log_file = self.logs_path / "system.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return

        # Log the event
        self.logger.info(f"New file detected: {event.src_path}")

        # Create structured task file
        self.create_structured_task(event.src_path)

        # Log in system log
        self.log_to_system(f"File watcher detected new file: {event.src_path}")

    def on_moved(self, event):
        """Handle file move events"""
        if event.is_directory:
            return

        # Log the event
        self.logger.info(f"File moved: {event.src_path} -> {event.dest_path}")
        self.log_to_system(f"File moved: {event.src_path} -> {event.dest_path}")

    def create_structured_task(self, file_path):
        """Create a structured task file in Needs_Action directory"""
        try:
            file_path = Path(file_path)

            # Read the content of the incoming file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create a structured task based on the incoming file
            task_id = f"task_{int(time.time())}_{file_path.stem}"
            task_file_path = self.needs_action_path / f"{task_id}.json"

            # Create structured task data
            task_data = {
                "id": task_id,
                "title": f"Process: {file_path.name}",
                "description": f"New file received: {file_path.name}",
                "source_file": str(file_path),
                "content_preview": content[:500] + "..." if len(content) > 500 else content,
                "created_at": datetime.now().isoformat(),
                "file_type": file_path.suffix.lower(),
                "status": "pending",
                "priority": "medium"  # Can be set based on content analysis
            }

            # Write the structured task to the Needs_Action directory
            with open(task_file_path, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2)

            self.logger.info(f"Created structured task: {task_file_path}")
            self.log_to_system(f"Created structured task from file: {file_path.name}")

        except Exception as e:
            self.logger.error(f"Error creating structured task from {file_path}: {e}")
            self.log_to_system(f"Error processing file {file_path}: {str(e)}")

    def log_to_system(self, message):
        """Log event to system log file"""
        log_file = self.logs_path / "system.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")


class FileWatcher:
    """File Watcher class to monitor incoming directory"""

    def __init__(self, incoming_path="./incoming", vault_path="./vault"):
        self.incoming_path = Path(incoming_path)
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.logs_path = Path("logs")

        # Ensure directories exist
        self.incoming_path.mkdir(exist_ok=True)
        self.needs_action_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

        # Initialize the event handler
        self.event_handler = FileWatcherHandler(self.incoming_path, self.vault_path)

        # Initialize the observer
        self.observer = Observer()

    def start(self):
        """Start watching the incoming directory"""
        self.observer.schedule(self.event_handler, str(self.incoming_path), recursive=False)
        self.observer.start()
        print(f"File watcher started, monitoring: {self.incoming_path}")

    def stop(self):
        """Stop watching the directory"""
        self.observer.stop()
        self.observer.join()
        print("File watcher stopped")

    def run(self):
        """Run the file watcher continuously"""
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()


if __name__ == "__main__":
    # For testing purposes
    watcher = FileWatcher()
    watcher.run()