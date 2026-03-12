#!/usr/bin/env python3
"""
send_optin.py — Manage opt-in consent status.

The primary opt-in method is the user texting JOIN to (310) 919-4684.
This script is for checking status and manually recording consent.

Usage:
    python send_optin.py --status              Show consent status
    python send_optin.py --approve +1XXXXXXXXXX  Manually record opt-in
"""

import sys
import json
from pathlib import Path
from consent import record_optin, get_status

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def show_status(config):
    print("\n📋 Consent Status\n" + "-" * 55)
    for r in config["recipients"]:
        phone = r["phone"]
        name = r.get("name", "???")
        status = get_status(phone)
        icon = {"opted_in": "✅", "opted_out": "❌", "pending": "⏳", "none": "—"}.get(status, "?")
        print(f"  {name:<15} {phone:<18} {icon} {status}")
    print()
    print("  Users opt in by texting JOIN to (310) 919-4684")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python send_optin.py --status                Show consent status")
        print("  python send_optin.py --approve +1XXXXXXXXXX  Manually record opt-in")
        print()
        print("  Primary opt-in: users text JOIN to (310) 919-4684")
        sys.exit(1)

    config = load_config()

    if sys.argv[1] == "--status":
        show_status(config)
    elif sys.argv[1] == "--approve" and len(sys.argv) >= 3:
        phone = sys.argv[2]
        if not phone.startswith("+"):
            phone = "+1" + phone.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")
        record_optin(phone)
        print(f"  ✅ Manually recorded opt-in for {phone}")
    else:
        print("Unknown command. Use --status or --approve +1XXXXXXXXXX")


if __name__ == "__main__":
    main()
