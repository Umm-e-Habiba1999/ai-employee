#!/usr/bin/env python3
"""
Test script to verify LinkedIn posting functionality
"""
import os
import json
from datetime import datetime
from pathlib import Path
import time

def test_linkedin_posting():
    """Test the LinkedIn posting functionality"""
    print("Testing LinkedIn posting functionality...")

    # Check if environment variables are set
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")

    if not linkedin_email or not linkedin_password:
        print("❌ ERROR: LINKEDIN_EMAIL or LINKEDIN_PASSWORD not set in .env file")
        print("Please add these to your .env file:")
        print("LINKEDIN_EMAIL=your_email@example.com")
        print("LINKEDIN_PASSWORD=your_password")
        return False

    print(f"✅ LinkedIn credentials are configured: {bool(linkedin_email)}")

    # Import required modules
    try:
        from utils.linkedin_poster import LinkedInPoster
        from utils.linkedin_watcher import LinkedInWatcher
        print("✅ Modules imported successfully")
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        return False

    # Test LinkedInPoster initialization
    try:
        logs_path = Path("./logs")
        poster = LinkedInPoster(logs_path)
        print("✅ LinkedInPoster initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing LinkedInPoster: {e}")
        return False

    # Test simple posting functionality with sample data
    sample_task_data = {
        'title': 'Test Task Completion',
        'description': 'Testing LinkedIn auto-posting functionality from AI Employee system',
        'file_name': 'test_approved_task.md',
        'file_path': './test/test_task.md'
    }

    print("\n--- Testing basic functionality ---")

    # Test content generation
    try:
        sample_content = poster.generate_business_post(
            sample_task_data['title'],
            sample_task_data['description']
        )
        print(f"✅ Content generated successfully: {len(sample_content)} characters")
        print(f"Sample: {sample_content[:100]}...")
    except Exception as e:
        print(f"❌ Error generating content: {e}")
        return False

    # Test the LinkedInWatcher as well
    try:
        watcher = LinkedInWatcher()
        print("✅ LinkedInWatcher initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing LinkedInWatcher: {e}")
        return False

    print("\n--- LinkedIn posting readiness check ---")
    print("✅ All required components are available")
    print("✅ Environment variables are configured")
    print("✅ Modules are importable")
    print("✅ Content generation works")

    return True

def test_approved_folder_workflow():
    """Test the workflow for approved tasks"""
    print("\n--- Testing Approved Folder Workflow ---")

    vault_path = Path("./vault")
    approved_path = vault_path / "Approved"
    pending_path = vault_path / "Pending_Approval"

    # Check if directories exist
    print(f"✅ Vault directory exists: {vault_path.exists()}")
    print(f"✅ Approved directory exists: {approved_path.exists()}")
    print(f"✅ Pending Approval directory exists: {pending_path.exists()}")

    # Check for any approved files
    if approved_path.exists():
        approved_files = list(approved_path.glob("*.md"))
        print(f"📊 Found {len(approved_files)} approved files")

        for file in approved_files:
            print(f"   - {file.name}")

    # Check for any pending approval files
    if pending_path.exists():
        pending_files = list(pending_path.glob("*.md"))
        print(f"📊 Found {len(pending_files)} pending approval files")

        for file in pending_files:
            print(f"   - {file.name} (check if it has approval marks: [x] or [X])")

    # Check logs
    logs_path = Path("./logs")
    if logs_path.exists():
        linkedin_watcher_log = logs_path / "linkedin_watcher.log"
        linkedin_poster_log = logs_path / "linkedin_poster.log"

        if linkedin_watcher_log.exists():
            print(f"✅ LinkedIn Watcher log exists: {linkedin_watcher_log}")
        else:
            print("⚠️  LinkedIn Watcher log does not exist yet")

        if linkedin_poster_log.exists():
            print(f"✅ LinkedIn Poster log exists: {linkedin_poster_log}")
        else:
            print("⚠️  LinkedIn Poster log does not exist yet")

def create_test_approval_task():
    """Create a test task that can be approved manually"""
    print("\n--- Creating Test Task ---")

    vault_path = Path("./vault")
    pending_path = vault_path / "Pending_Approval"
    pending_path.mkdir(exist_ok=True)

    task_id = f"test_approval_task_{int(datetime.now().timestamp())}"
    task_file = pending_path / f"{task_id}.md"

    task_content = f"""# Draft Action Plan

**Generated from Plan:** {task_id}.json
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Plan Summary

This is a test task to verify LinkedIn posting functionality.

## Action Status
- [ ] Pending Approval
- [ ] Ready for Execution (after approval)
- [ ] In Progress
- [ ] Completed

## Approval Section
**Approve this action?**
- [x] Yes, proceed with execution  <!-- Manually check this box to approve -->
- [ ] No, reject this action
- [ ] Modify before approval

**Approver Notes:**
Test task for verifying LinkedIn posting workflow.

## Execution Log
**Execution Steps:**
1. [ ] Review this draft
2. [ ] Make approval decision
3. [ ] Move to Approved folder (to execute) or Rejected folder (to discard)
4. [ ] Monitor execution if approved
"""

    with open(task_file, 'w', encoding='utf-8') as f:
        f.write(task_content)

    print(f"✅ Created test task: {task_file.name}")
    print(f"📝 To test: Edit the file and change '[ ] Yes, proceed with execution' to '[x] Yes, proceed with execution'")
    print(f"📁 Location: {task_file}")

    return task_file

def check_posting_logs():
    """Check the posting logs for recent activity"""
    print("\n--- Checking Posting Logs ---")

    logs_path = Path("./logs")

    # Check LinkedIn Watcher log
    watcher_log = logs_path / "linkedin_watcher.log"
    if watcher_log.exists():
        print(f"\n📄 LinkedIn Watcher Log ({watcher_log}):")
        try:
            with open(watcher_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show last 10 lines
                for line in lines[-10:]:
                    print(f"   {line.strip()}")
        except Exception as e:
            print(f"   Error reading log: {e}")
    else:
        print(f"\n⚠️  LinkedIn Watcher log not found: {watcher_log}")

    # Check LinkedIn Poster log
    poster_log = logs_path / "linkedin_poster.log"
    if poster_log.exists():
        print(f"\n📄 LinkedIn Poster Log ({poster_log}):")
        try:
            with open(poster_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show last 10 lines
                for line in lines[-10:]:
                    print(f"   {line.strip()}")
        except Exception as e:
            print(f"   Error reading log: {e}")
    else:
        print(f"\n⚠️  LinkedIn Poster log not found: {poster_log}")

    # Check system log
    system_log = logs_path / "system.log"
    if system_log.exists():
        print(f"\n📄 System Log ({system_log}) - LinkedIn related entries:")
        try:
            with open(system_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show last 20 lines with LinkedIn mentions
                linkedin_lines = [line for line in lines[-20:] if 'LinkedIn' in line]
                if linkedin_lines:
                    for line in linkedin_lines:
                        print(f"   {line.strip()}")
                else:
                    print("   No LinkedIn-related entries found in recent logs")
        except Exception as e:
            print(f"   Error reading log: {e}")

def print_test_instructions():
    """Print detailed instructions for testing"""
    print("\n" + "="*60)
    print("📋 DETAILED TESTING INSTRUCTIONS")
    print("="*60)
    print("\n1. RUN THE SILVER TIER SYSTEM:")
    print("   python silver_tier_coordinator.py --mode continuous")

    print("\n2. PREPARE THE TEST:")
    print("   - Make sure your LinkedIn credentials are in .env file")
    print("   - Ensure the Silver Tier system is running continuously")
    print("   - The LinkedInWatcher should be monitoring the Approved folder")

    print("\n3. CREATE AN APPROVED TASK:")
    print("   - Either use the auto-generated test task created by this script")
    print("   - OR manually move a task from Pending_Approval to Approved")
    print("   - OR ensure a task in Pending_Approval has '[x] Yes, proceed with execution'")

    print("\n4. VERIFY THE FLOW:")
    print("   - Check that the file appears in vault/Approved")
    print("   - Wait for LinkedInWatcher to process it (up to 30 seconds)")
    print("   - Check logs for posting success/failure messages")
    print("   - Verify the file moves to vault/Done after successful posting")
    print("   - Check your LinkedIn account for the new post")

    print("\n5. CHECK LOGS:")
    print("   - logs/linkedin_watcher.log")
    print("   - logs/linkedin_poster.log")
    print("   - logs/system.log")

    print("\n6. TROUBLESHOOTING:")
    print("   - If no posts appear, check credentials in .env")
    print("   - If files disappear without posting, check for race conditions")
    print("   - If posting fails, check network connectivity and LinkedIn site access")

def main():
    """Main function to run all tests"""
    print("🔍 LinkedIn Posting Functionality Test")
    print("="*50)

    # Test basic functionality
    success = test_linkedin_posting()

    if success:
        # Check current workflow state
        test_approved_folder_workflow()

        # Create a test task
        create_test_approval_task()

        # Check existing logs
        check_posting_logs()

        # Print instructions
        print_test_instructions()

        print(f"\n✅ Testing setup complete!")
        print("Now run the Silver Tier system to test the actual posting functionality.")
    else:
        print(f"\n❌ Testing failed - please address the issues above")

    return success

if __name__ == "__main__":
    main()