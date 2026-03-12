#!/usr/bin/env python3
"""
webhook.py — Handle incoming SMS replies for opt-in consent.

Flow:
  1. User texts JOIN/ALERTS/SUBSCRIBE to your Twilio number
  2. System replies with opt-in confirmation
  3. User replies YES to confirm
  4. Alerts begin

Deploy alongside monitor.py on your VPS.

Setup:
  1. pip install flask
  2. python webhook.py  (runs on port 5000)
  3. In Twilio Console -> Phone Numbers -> your number -> Messaging:
     Set "A message comes in" webhook URL to: http://YOUR_VPS_IP:5000/sms
"""

import json
import logging
from pathlib import Path
from flask import Flask, request
from consent import record_optin, record_optout, record_pending, get_status

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("webhook")

CONFIG_PATH = Path(__file__).parent / "config.json"

JOIN_KEYWORDS = {"JOIN", "ALERTS", "SUBSCRIBE", "START"}

OPTIN_CONFIRMATION = (
    "MiLB Game Alerts: You've requested to receive real-time minor league "
    "baseball player stats via text. Reply YES to confirm your subscription "
    "or NO to decline. Msg frequency varies. Msg & data rates may apply. "
    "Reply STOP anytime to cancel. "
    "Terms: https://mdruyanoff.github.io/milb-alerts/terms.html "
    "Privacy: https://mdruyanoff.github.io/milb-alerts/privacy.html"
)

SUBSCRIBED_CONFIRMATION = (
    "You're subscribed to MiLB Game Alerts from (310) 919-4684! "
    "You'll receive player stats when games finish. Msg frequency varies. "
    "Msg & data rates may apply. Reply STOP to unsubscribe, HELP for help."
)

HELP_MESSAGE = (
    "MiLB Game Alerts from (310) 919-4684. Baseball player stats via text. "
    "Msg frequency varies. Msg & data rates may apply. Reply STOP to unsubscribe. "
    "Terms: https://mdruyanoff.github.io/milb-alerts/terms.html "
    "Privacy: https://mdruyanoff.github.io/milb-alerts/privacy.html"
)


def _twiml(text):
    """Wrap reply text in TwiML."""
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Message>{text}</Message></Response>',
        200,
        {"Content-Type": "text/xml"},
    )


def _twiml_empty():
    return '<Response></Response>', 200, {"Content-Type": "text/xml"}


@app.route("/sms", methods=["POST"])
def incoming_sms():
    from_number = request.form.get("From", "")
    body = request.form.get("Body", "").strip().upper()

    logger.info(f"Incoming SMS from {from_number}: {body}")
    status = get_status(from_number)

    # --- JOIN keywords: user initiates opt-in ---
    if body in JOIN_KEYWORDS:
        record_pending(from_number)
        logger.info(f"JOIN received from {from_number} — sending opt-in confirmation")
        return _twiml(OPTIN_CONFIRMATION)

    # --- YES: confirm subscription ---
    if body in ("YES", "Y", "OPTIN", "OPT IN"):
        record_optin(from_number)
        logger.info(f"Opt-in confirmed for {from_number}")
        return _twiml(SUBSCRIBED_CONFIRMATION)

    # --- NO: decline ---
    if body in ("NO", "N"):
        if status == "pending":
            record_optout(from_number)
            logger.info(f"Opt-in declined by {from_number}")
            return _twiml("Got it — you won't receive any alerts from MiLB Game Alerts.")
        return _twiml("Reply JOIN to subscribe to MiLB Game Alerts, or STOP to unsubscribe.")

    # --- STOP: Twilio handles this at carrier level, but we record locally ---
    if body in ("STOP", "STOPALL", "UNSUBSCRIBE", "CANCEL", "END", "QUIT"):
        record_optout(from_number)
        logger.info(f"Opt-out recorded for {from_number}")
        return _twiml_empty()  # Twilio sends its own STOP confirmation

    # --- HELP ---
    if body in ("HELP", "INFO"):
        return _twiml(HELP_MESSAGE)

    # --- Unknown: guide them ---
    return _twiml(
        "MiLB Game Alerts: Reply JOIN to subscribe, STOP to unsubscribe, or HELP for info."
    )


@app.route("/health", methods=["GET"])
def health():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
