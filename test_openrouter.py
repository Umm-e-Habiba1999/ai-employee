#!/usr/bin/env python3
"""
Test script to verify OpenRouter integration
"""

import sys
import os
sys.path.append('./utils')

from utils.openrouter_client import OpenRouterClient

def test_openrouter_client():
    print("Testing OpenRouter Client Integration...")

    # Create client instance
    client = OpenRouterClient()

    print(f"API Key configured: {'Yes' if client.api_key else 'No'}")
    print(f"DRY_RUN mode: {client.dry_run}")
    print(f"Connected: {client.is_connected()}")
    print(f"Client Info: {client.get_client_info()}")

    # Test connection status for dashboard
    mode = "LIVE" if not client.dry_run and client.api_key else "DRY_RUN"
    connected_services = client.get_client_info()

    print(f"\nDashboard values:")
    print(f"Mode: {mode}")
    print(f"Connected Services: {connected_services}")

    # The desired output when connected:
    if client.api_key and not client.dry_run:
        expected_mode = "LIVE"
        expected_services = "Claude (OpenRouter)"
        print(f"\nWith OPENROUTER_API_KEY set and DRY_RUN=false:")
        print(f"  Mode should be: {expected_mode}")
        print(f"  Connected Services should be: {expected_services}")
    else:
        print(f"\nWith current settings:")
        print(f"  Mode: {mode}")
        print(f"  Connected Services: {connected_services}")

    return True

if __name__ == "__main__":
    test_openrouter_client()