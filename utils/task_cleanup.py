#!/usr/bin/env python3
"""
Task Cleanup Utility for AI Employee Silver Tier System
Removes duplicate tasks and fixes task lifecycle issues
"""
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import re

def deduplicate_tasks():
    """Remove duplicate task files in Needs_Action"""
    print("Starting task deduplication...")
    vault_path = Path("E:/hackathon0/ai-employee/vault")
    needs_action_path = vault_path / "Needs_Action"

    task_files = list(needs_action_path.glob("*.json"))
    seen_ids = set()
    duplicates = []

    for task_file in task_files:
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            task_id = task_data.get('id', str(task_file))

            if task_id in seen_ids:
                duplicates.append(task_file)
                print(f"  Found duplicate: {task_file.name}")
            else:
                seen_ids.add(task_id)
        except Exception as e:
            print(f"  Error reading {task_file.name}: {e}")

    # Remove duplicates
    for dup in duplicates:
        dup_path = needs_action_path / dup
        if dup_path.exists():
            backup_path = vault_path / "Backup"
            backup_path.mkdir(exist_ok=True)
            backup_file = backup_path / f"removed_duplicate_{dup.name}"
            shutil.move(str(dup_path), str(backup_file))
            print(f"  Moved duplicate to backup: {backup_file.name}")

    print(f"Removed {len(duplicates)} duplicate task files")


def deduplicate_plans():
    """Remove duplicate plan files in Plans"""
    print("Starting plan deduplication...")
    vault_path = Path("E:/hackathon0/ai-employee/vault")
    plans_path = vault_path / "Plans"

    plan_files = list(plans_path.glob("*.md"))
    seen_names = set()
    duplicates = []

    for plan_file in plan_files:
        if plan_file.name in seen_names:
            duplicates.append(plan_file)
            print(f"  Found duplicate plan: {plan_file.name}")
        else:
            seen_names.add(plan_file.name)

    # Remove duplicates
    for dup in duplicates:
        dup_path = plans_path / dup
        if dup_path.exists():
            backup_path = vault_path / "Backup"
            backup_path.mkdir(exist_ok=True)
            backup_file = backup_path / f"removed_duplicate_plan_{dup.name}"
            shutil.move(str(dup_path), str(backup_file))
            print(f"  Moved duplicate plan to backup: {backup_file.name}")

    print(f"Removed {len(duplicates)} duplicate plan files")


def deduplicate_done():
    """Remove duplicate files in Done"""
    print("Starting Done folder deduplication...")
    vault_path = Path("E:/hackathon0/ai-employee/vault")
    done_path = vault_path / "Done"

    if not done_path.exists():
        print("  Done folder doesn't exist")
        return

    done_files = list(done_path.glob("*.md"))
    seen_names = set()
    duplicates = []

    for done_file in done_files:
        # For completed files, we should consider timestamp in the name as part of uniqueness
        # So we'll use the full name with timestamp as unique identifier
        # However, if we find files with same base name (just different timestamps), that's okay
        # We're looking for truly duplicated files without timestamps
        base_name = done_file.stem

        # For completed files that don't have timestamp, they should be considered duplicates
        if re.match(r'^completed_.*', base_name):
            # Extract the base plan name after "completed_YYYYMMDD_HHMMSS_"
            match = re.match(r'^completed_\d+_\d+_(.+)', base_name)
            if match:
                actual_base_name = match.group(1)
                if actual_base_name in seen_names:
                    duplicates.append(done_file)
                    print(f"  Found duplicate in Done: {done_file.name}")
                    continue

        seen_names.add(base_name)

    # Remove duplicates
    for dup in duplicates:
        dup_path = done_path / dup
        if dup_path.exists():
            backup_path = vault_path / "Backup"
            backup_path.mkdir(exist_ok=True)
            backup_file = backup_path / f"removed_duplicate_done_{dup.name}"
            shutil.move(str(dup_path), str(backup_file))
            print(f"  Moved duplicate from Done to backup: {backup_file.name}")

    print(f"Removed {len(duplicates)} duplicate files from Done")


def fix_workflow_state():
    """Fix various workflow state issues"""
    print("Fixing workflow state issues...")

    # Check for tasks that are missing plan references
    vault_path = Path("E:/hackathon0/ai-employee/vault")
    needs_action_path = vault_path / "Needs_Action"
    plans_path = vault_path / "Plans"

    task_files = list(needs_action_path.glob("*.json"))

    for task_file in task_files:
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            # If status is processed but no plan exists, fix the status
            if task_data.get('status') == 'processed' and task_data.get('plan_generated'):
                plan_id = task_data['plan_generated']
                plan_file = plans_path / f"{plan_id}.md"

                if not plan_file.exists():
                    print(f"  Task marked as processed but plan doesn't exist: {task_file.name}")
                    # Reset status to pending since plan doesn't exist
                    task_data['status'] = 'pending'
                    task_data['processing_completed'] = False
                    task_data['plan_generated'] = None
                    task_data['processed_at'] = None

                    with open(task_file, 'w', encoding='utf-8') as f:
                        json.dump(task_data, f, indent=2)
                    print(f"    Reset status to pending")
        except Exception as e:
            print(f"  Error fixing workflow state for {task_file.name}: {e}")


def main():
    print("AI Employee Silver Tier Task Cleanup Utility")
    print("=" * 50)

    deduplicate_tasks()
    print()

    deduplicate_plans()
    print()

    deduplicate_done()
    print()

    fix_workflow_state()
    print()

    print("Cleanup complete!")


if __name__ == "__main__":
    main()