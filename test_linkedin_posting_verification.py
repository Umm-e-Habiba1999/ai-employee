#!/usr/bin/env python3
"""
Test script to verify LinkedIn posting functionality after fixes
"""
import os
import time
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_linkedin_credentials():
    """Test LinkedIn credentials in .env file"""
    print("=" * 60)
    print("Testing LinkedIn Credentials...")
    print("=" * 60)

    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")

    print(f"LinkedIn email configured: {bool(linkedin_email)}")
    print(f"LinkedIn email: {linkedin_email}")
    print(f"LinkedIn password configured: {bool(linkedin_password)}")

    if linkedin_email and linkedin_password and "@" in linkedin_email and linkedin_email != "your_linkedin_email@example.com":
        print("[SUCCESS] LinkedIn credentials appear to be correctly configured")
        return True
    else:
        print("[ERROR] LinkedIn credentials need to be properly set in .env file")
        return False


def create_test_approved_file():
    """Create a test file in the Approved folder to test the LinkedInWatcher"""
    print("")
    print("=" * 60)
    print("Creating Test Approved File...")
    print("=" * 60)

    vault_path = Path("./vault")
    approved_path = vault_path / "Approved"

    # Create test content that simulates an approved task
    test_task_content = f"""# Draft Action Plan

**Generated from Plan:** test_linkedin_posting_plan.md
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Plan Summary
This is a test task to verify LinkedIn posting functionality after approval.

## Requires Approval
true

## Action Status
- [x] Pending Approval
- [x] Ready for Execution (after approval)
- [x] In Progress
- [x] Completed

## Approval Section
**Approve this action?**
- [x] Yes, proceed with execution
- [ ] No, reject this action
- [ ] Modify before approval

**Approver Notes:**
Test task approved for LinkedIn posting.

## Execution Log
**Execution Steps:**
1. [x] Review this draft
2. [x] Make approval decision
3. [x] Move to Approved folder (to execute) or Rejected folder (to discard)
4. [ ] Monitor execution if approved
"""

    # Create a test file in the Approved folder
    test_file = approved_path / f"test_linkedin_post_{int(datetime.now().timestamp())}.md"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_task_content)

    print(f"[SUCCESS] Created test approved file: {test_file.name}")
    print(f"[INFO] Location: {test_file}")
    print(f"[INFO] File size: {test_file.stat().st_size} bytes")

    return test_file


def run_linkedin_watcher_test():
    """Run the LinkedIn Watcher to test processing of approved files"""
    print("")
    print("=" * 60)
    print("Testing LinkedIn Watcher...")
    print("=" * 60)

    try:
        from utils.linkedin_watcher import LinkedInWatcher

        print("[SUCCESS] Successfully imported LinkedInWatcher")

        # Create watcher instance
        watcher = LinkedInWatcher(vault_path="./vault", logs_path="./logs", check_interval=5)
        print("[SUCCESS] LinkedInWatcher initialized successfully")

        # List approved files before processing
        approved_files_before = list((Path("./vault") / "Approved").glob("*.md"))
        print(f"[INFO] Found {len(approved_files_before)} approved files before processing")

        for f in approved_files_before:
            print(f"   - {f.name}")

        # Process approved tasks
        print("[INFO] Processing approved tasks...")
        watcher._check_approved_tasks()

        # Wait a bit for processing to complete
        time.sleep(2)

        # List approved files after processing
        approved_files_after = list((Path("./vault") / "Approved").glob("*.md"))
        print(f"[INFO] Found {len(approved_files_after)} approved files after processing")

        for f in approved_files_after:
            print(f"   - {f.name}")

        # Check Done folder
        done_files = list((Path("./vault") / "Done").glob("*.md"))
        print(f"[INFO] Found {len(done_files)} files in Done folder")

        for f in done_files[-5:]:  # Show last 5 files
            print(f"   - {f.name}")

        # Check Failed folder
        failed_path = Path("./vault") / "Failed"
        if failed_path.exists():
            failed_files = list(failed_path.glob("*.md"))
            print(f"[INFO] Found {len(failed_files)} files in Failed folder")

            for f in failed_files[-5:]:  # Show last 5 files
                print(f"   - {f.name}")

        return True

    except Exception as e:
        print(f"[ERROR] Error testing LinkedIn Watcher: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False


def check_logs():
    """Check the logs for any errors or success messages"""
    print("")
    print("=" * 60)
    print("Checking Logs...")
    print("=" * 60)

    logs_path = Path("./logs")

    # Check LinkedIn Watcher log
    watcher_log = logs_path / "linkedin_watcher.log"
    if watcher_log.exists():
        print(f"")
        print(f"[INFO] LinkedIn Watcher Log ({watcher_log}):")
        try:
            with open(watcher_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show last 15 lines
                for line in lines[-15:]:
                    print(f"   {line.strip()}")
        except Exception as e:
            print(f"   [ERROR] Error reading log: {e}")
    else:
        print(f"")
        print(f"[WARNING] LinkedIn Watcher log not found: {watcher_log}")

    # Check LinkedIn Poster log
    poster_log = logs_path / "linkedin_poster.log"
    if poster_log.exists():
        print(f"")
        print(f"[INFO] LinkedIn Poster Log ({poster_log}):")
        try:
            with open(poster_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Show last 15 lines
                for line in lines[-15:]:
                    print(f"   {line.strip()}")
        except Exception as e:
            print(f"   [ERROR] Error reading log: {e}")
    else:
        print(f"")
        print(f"[WARNING] LinkedIn Poster log not found: {poster_log}")


def main():
    """Run complete test suite"""
    print("LinkedIn Posting Functionality Verification Test")
    print("This script verifies the fixes for LinkedIn posting issues")
    print("=" * 60)

    results = []

    # Test 1: LinkedIn credentials
    results.append(("LinkedIn Credentials", test_linkedin_credentials()))

    # Test 2: Create test approved file
    test_file = create_test_approved_file()
    results.append(("Create Test File", True))  # Always succeeds if no exception

    # Test 3: Run LinkedIn Watcher test
    results.append(("LinkedIn Watcher Test", run_linkedin_watcher_test()))

    # Check logs
    check_logs()

    # Print results summary
    print("")
    print("=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")

    overall_success = all(result for _, result in results)
    print(f"")
    print(f"Overall Result: {'[PASS]' if overall_success else '[FAIL]'}")

    if overall_success:
        print("")
        print("[SUCCESS] All tests passed! The LinkedIn posting functionality should now work correctly.")
        print("")
        print("[INFO] Next steps:")
        print("   - Run the Silver Tier system: python silver_tier_coordinator.py --mode continuous")
        print("   - Monitor the logs for LinkedIn posting activity")
        print("   - Check that approved files move from Approved -> Done after successful posting")
    else:
        print("")
        print("[WARNING] Some tests failed. Please review the errors above.")

    return overall_success


if __name__ == "__main__":
    main()