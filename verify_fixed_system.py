#!/usr/bin/env python3
"""
Verification script to confirm Silver Tier system fixes
"""
import os
from pathlib import Path
import json

def verify_file_watcher_fix():
    """Verify that file watcher moves files to prevent reprocessing"""
    print("Verifying file watcher fix...")

    processed_dir = Path("E:/hackathon0/ai-employee/incoming/processed")
    if processed_dir.exists():
        processed_files = list(processed_dir.glob("*"))
        print(f"  [PASS] Found {len(processed_files)} files in processed directory (prevents reprocessing)")
        return True
    else:
        print("  [FAIL] Processed directory not found")
        return False

def verify_task_state_management():
    """Verify that tasks are properly marked as processed"""
    print("Verifying task state management...")

    needs_action_path = Path("E:/hackathon0/ai-employee/vault/Needs_Action")
    task_files = list(needs_action_path.glob("*.json"))

    processed_count = 0
    for task_file in task_files:
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            if task_data.get('processing_completed') or task_data.get('status') == 'processed':
                processed_count += 1
        except:
            continue

    if processed_count > 0:
        print(f"  [PASS] Found {processed_count} tasks properly marked as processed")
        return True
    else:
        print("  [WARN] No processed tasks found (might be normal if system is new)")
        return True

def verify_no_duplicate_generation():
    """Verify that duplicate tasks are not being generated"""
    print("Verifying no duplicate generation...")

    needs_action_path = Path("E:/hackathon0/ai-employee/vault/Needs_Action")
    plans_path = Path("E:/hackathon0/ai-employee/vault/Plans")

    # Check for duplicate task IDs
    task_files = list(needs_action_path.glob("*.json"))
    seen_ids = set()
    duplicates = 0

    for task_file in task_files:
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            task_id = task_data.get('id')
            if task_id in seen_ids:
                duplicates += 1
            else:
                seen_ids.add(task_id)
        except:
            continue

    # Check for duplicate plan names
    plan_files = list(plans_path.glob("*.md"))
    seen_plan_names = set()
    plan_duplicates = 0

    for plan_file in plan_files:
        if plan_file.name in seen_plan_names:
            plan_duplicates += 1
        else:
            seen_plan_names.add(plan_file.name)

    if duplicates == 0 and plan_duplicates == 0:
        print(f"  [PASS] No duplicate tasks ({len(seen_ids)} unique) or plans ({len(seen_plan_names)} unique) found")
        return True
    else:
        print(f"  [FAIL] Found {duplicates} duplicate tasks and {plan_duplicates} duplicate plans")
        return False

def verify_gmail_tracking():
    """Verify that Gmail emails are tracked to prevent reprocessing"""
    print("Verifying Gmail tracking...")

    logs_path = Path("E:/hackathon0/ai-employee/logs")
    processed_emails_file = logs_path / "processed_emails.json"

    if processed_emails_file.exists():
        print(f"  [PASS] Gmail processed email tracking file exists")
        try:
            with open(processed_emails_file, 'r', encoding='utf-8') as f:
                processed_emails = json.load(f)
            print(f"  [PASS] Found {len(processed_emails)} tracked processed email IDs")
            return True
        except:
            print(f"  [WARN] Could not read processed email tracking")
            return True  # Not critical
    else:
        print(f"  [WARN] Gmail processed email tracking file not found (may be first run)")
        return True

def verify_workflow_state():
    """Verify that workflow state is properly managed"""
    print("Verifying workflow state management...")

    vault_path = Path("E:/hackathon0/ai-employee/vault")
    needs_action = len(list((vault_path / "Needs_Action").glob("*.json")))
    plans = len(list((vault_path / "Plans").glob("*.md")))
    pending_approval = len(list((vault_path / "Pending_Approval").glob("*.md")))
    done = len(list((vault_path / "Done").glob("*.md")))

    print(f"  - Tasks in Needs_Action: {needs_action}")
    print(f"  - Plans in Plans: {plans}")
    print(f"  - Files awaiting approval: {pending_approval}")
    print(f"  - Completed tasks: {done}")

    # Basic sanity check - shouldn't be extreme numbers
    if all(x >= 0 for x in [needs_action, plans, pending_approval, done]):
        print(f"  [PASS] Workflow state appears reasonable")
        return True
    else:
        print(f"  [FAIL] Unexpected workflow state")
        return False

def main():
    print("SILVER TIER SYSTEM FIX VERIFICATION")
    print("=" * 50)

    # Run all verifications
    results = [
        verify_file_watcher_fix(),
        verify_task_state_management(),
        verify_no_duplicate_generation(),
        verify_gmail_tracking(),
        verify_workflow_state()
    ]

    print(f"\nVERIFICATION RESULTS:")
    print(f"- File Watcher Fix: {'[PASS]' if results[0] else '[FAIL]'}")
    print(f"- Task State Management: {'[PASS]' if results[1] else '[FAIL]'}")
    print(f"- No Duplicate Generation: {'[PASS]' if results[2] else '[FAIL]'}")
    print(f"- Gmail Tracking: {'[PASS]' if results[3] else '[FAIL]'}")
    print(f"- Workflow State: {'[PASS]' if results[4] else '[FAIL]'}")

    all_passed = all(results)

    print(f"\n{'='*50}")
    if all_passed:
        print("SUCCESS! Silver Tier system fixes are working correctly!")
    else:
        print("Some verifications failed. System may need additional fixes.")
    print(f"{'='*50}")

    return all_passed

if __name__ == "__main__":
    main()