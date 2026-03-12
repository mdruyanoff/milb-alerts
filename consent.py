"""
consent.py — Track SMS opt-in/opt-out consent.

Stores consent status in consent.json alongside config.json.
Twilio handles STOP/UNSUBSCRIBE automatically at the carrier level,
but we also track it locally for our records.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

CONSENT_PATH = Path(__file__).parent / "consent.json"


def _load():
    if not CONSENT_PATH.exists():
        return {}
    with open(CONSENT_PATH) as f:
        return json.load(f)


def _save(data):
    with open(CONSENT_PATH, "w") as f:
        json.dump(data, f, indent=4)


def record_optin(phone: str):
    """Record that a phone number has opted in."""
    data = _load()
    data[phone] = {
        "status": "opted_in",
        "opted_in_at": datetime.now(timezone.utc).isoformat(),
        "opted_out_at": None,
    }
    _save(data)


def record_optout(phone: str):
    """Record that a phone number has opted out."""
    data = _load()
    if phone in data:
        data[phone]["status"] = "opted_out"
        data[phone]["opted_out_at"] = datetime.now(timezone.utc).isoformat()
    else:
        data[phone] = {
            "status": "opted_out",
            "opted_in_at": None,
            "opted_out_at": datetime.now(timezone.utc).isoformat(),
        }
    _save(data)


def record_pending(phone: str):
    """Record that an opt-in request was sent but not yet confirmed."""
    data = _load()
    data[phone] = {
        "status": "pending",
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "opted_in_at": None,
        "opted_out_at": None,
    }
    _save(data)


def is_consented(phone: str) -> bool:
    """Check if a phone number has active consent."""
    data = _load()
    entry = data.get(phone)
    if not entry:
        return False
    return entry.get("status") == "opted_in"


def get_status(phone: str) -> str:
    """Get consent status: 'opted_in', 'opted_out', 'pending', or 'none'."""
    data = _load()
    entry = data.get(phone)
    if not entry:
        return "none"
    return entry.get("status", "none")


def get_all() -> dict:
    """Get all consent records."""
    return _load()
