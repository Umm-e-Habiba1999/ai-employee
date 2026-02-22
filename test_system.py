#!/usr/bin/env python3
"""
Test script to verify AI Employee system components
"""

import os
import sys
from pathlib import Path

def test_directories():
    """Test that all required directories exist"""
    vault_path = Path("./vault")
    required_dirs = [
        "Needs_Action",
        "Plans",
        "Done",
        "Logs",
        "Pending_Approval",
        "Approved",
        "Rejected",
        "Accounting",
        "Briefings",
        "Active_Projects",
        "Skills",
        "Sub_Agents"
    ]

    print("Testing directory structure...")
    all_good = True

    for dir_name in required_dirs:
        dir_path = vault_path / dir_name
        if dir_path.exists():
            print(f"  [PASS] {dir_name}/ directory exists")
        else:
            print(f"  [FAIL] {dir_name}/ directory missing")
            all_good = False

    return all_good

def test_core_files():
    """Test that core files exist"""
    print("\nTesting core files...")
    all_good = True

    required_files = [
        "vault/Dashboard.md",
        "vault/Company_Handbook.md",
        "vault/Business_Goals.md",
        "skills/inbox_processor.py",
        "skills/approval_manager.py",
        "skills/dashboard_updater.py",
        "skills/audit_logger.py",
        "skills/weekly_ceo_briefing.py",
        "skills/task_completion_checker.py",
        "sub_agents/Communications_Agent.py",
        "sub_agents/Finance_Agent.py",
        "sub_agents/Operations_Agent.py",
        "sub_agents/CEO_Agent.py",
        "main.py",
        "README.md",
        ".env.example",
        "requirements.txt",
        "config.json"
    ]

    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"  [PASS] {file_path} exists")
        else:
            print(f"  [FAIL] {file_path} missing")
            all_good = False

    return all_good

def test_skills_import():
    """Test that skills can be imported"""
    print("\nTesting skill imports...")
    all_good = True

    # Add skills directory to path
    sys.path.insert(0, './skills')

    skills_to_test = [
        'inbox_processor',
        'approval_manager',
        'dashboard_updater',
        'audit_logger',
        'weekly_ceo_briefing',
        'task_completion_checker'
    ]

    for skill in skills_to_test:
        try:
            module = __import__(skill)
            print(f"  [PASS] {skill} imported successfully")
        except ImportError as e:
            print(f"  [FAIL] {skill} import failed: {e}")
            all_good = False

    return all_good

def test_agents_import():
    """Test that agents can be imported"""
    print("\nTesting agent imports...")
    all_good = True

    # Add sub_agents directory to path
    sys.path.insert(0, './sub_agents')

    agents_to_test = [
        'Communications_Agent',
        'Finance_Agent',
        'Operations_Agent',
        'CEO_Agent'
    ]

    for agent in agents_to_test:
        try:
            module = __import__(agent)
            print(f"  [PASS] {agent} imported successfully")
        except ImportError as e:
            print(f"  [FAIL] {agent} import failed: {e}")
            all_good = False

    return all_good

def main():
    print("AI Employee System - Comprehensive Test")
    print("="*50)

    dir_test = test_directories()
    file_test = test_core_files()
    skill_test = test_skills_import()
    agent_test = test_agents_import()

    print("\n" + "="*50)
    print("Test Summary:")
    print(f"  Directories: {'PASS' if dir_test else 'FAIL'}")
    print(f"  Core Files: {'PASS' if file_test else 'FAIL'}")
    print(f"  Skills Import: {'PASS' if skill_test else 'FAIL'}")
    print(f"  Agents Import: {'PASS' if agent_test else 'FAIL'}")

    overall = all([dir_test, file_test, skill_test, agent_test])
    print(f"\nOverall Result: {'PASS' if overall else 'FAIL'}")

    if overall:
        print("\n[SUCCESS] AI Employee system is properly structured and ready to use!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and add your credentials")
        print("2. Install required packages: pip install -r requirements.txt")
        print("3. Add tasks to vault/Needs_Action/ to get started")
        print("4. Run with: python main.py")
    else:
        print("\n[FAILURE] System has issues that need to be resolved before use.")

    return overall

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)