#!/usr/bin/env python3
"""
Test script for Silver Tier functionality
"""
import time
import shutil
from pathlib import Path

def test_silver_tier():
    """Test the Silver Tier functionality"""
    from silver_tier_coordinator import SilverTierCoordinator

    print("Testing Silver Tier functionality...")

    # Create a coordinator instance
    coordinator = SilverTierCoordinator()

    # Run one cycle to process any existing files
    print("Running one workflow cycle...")
    coordinator.run_once()

    print("Silver Tier test completed.")

def test_file_watcher():
    """Test the file watcher by creating a test file"""
    from utils.file_watcher import FileWatcher
    import time

    print("Testing File Watcher...")

    # Create a test file in the incoming directory
    incoming_path = Path("incoming")
    test_file = incoming_path / "test_file.txt"

    with open(test_file, 'w') as f:
        f.write("This is a test file for the file watcher.")

    print(f"Created test file: {test_file}")

    # Give the file watcher a moment to process
    time.sleep(2)

    # Check if a structured task was created in Needs_Action
    needs_action_path = Path("vault") / "Needs_Action"
    task_files = list(needs_action_path.glob("task_*.json"))

    if task_files:
        print(f"Found structured task files: {task_files}")
        for task_file in task_files[-3:]:  # Show last 3 files if any
            print(f"  - {task_file.name}")
    else:
        print("No structured task files found in Needs_Action")

    # Clean up test file
    if test_file.exists():
        test_file.unlink()

if __name__ == "__main__":
    print("Starting Silver Tier tests...")

    # Test the file watcher first
    test_file_watcher()

    # Test the coordinator
    test_silver_tier()

    print("All tests completed!")