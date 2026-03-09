# MiLB Game Alerts

Real-time text message notifications with player stats the minute Minor League Baseball games finish.

Track specific players across all MiLB levels (AAA, AA, High-A, Single-A) and MLB Spring Training. When a game ends and your player was in it, you get a text within 60 seconds.

## How It Works

The system polls MLB's public Stats API every 60 seconds for game status changes. When a game transitions to "Final," it pulls the boxscore, extracts stats for your watched players, and sends formatted SMS alerts through Twilio.

Players are tracked by their MLB ID — not by team. If a player gets promoted, demoted, or traded, alerts continue with no configuration change.

## Example Alerts

**Hitters:**
```
Esteury Ruiz MLB/MIA @ HOU
1-3 | R, BB, SB

Jackson Ferris MLB/CHC @ SD
0-4 | 3 K
Reply STOP to unsubscribe
```

**Pitchers:**
```
Germán Márquez MLB/SD vs CHC
(W) 3.0 IP, 2 H, 0 R, 0 ER, 3 K, 0 BB, 0 HR
Reply STOP to unsubscribe
```

Every message includes an opt-out footer.

**Hitter stat rules:**
- `H-AB` always shown
- Singles (1B) not displayed
- Count of 1 omits the number: `R` not `1 R`, `2B` not `1 2B`
- Count >1 shows the number: `2 R`, `2 2B`, `3 K`
- Zero stats hidden entirely

**Pitcher stat rules:**
- Decision (W/L/SV) shown if applicable
- All game line stats shown (IP, H, R, ER, K, BB, HR)

## SMS Consent (Opt-In / Opt-Out)

This project includes a full TCPA-compliant consent system. No alerts are sent until a recipient explicitly opts in.

### How opt-in works

1. You add a contact and their players via `manage.py`
2. You send them an opt-in request:
   ```bash
   python send_optin.py Matt        # send to one person
   python send_optin.py all         # send to everyone who hasn't opted in
   ```
3. They receive a text:
   > MiLB Game Alerts: You've been invited to receive real-time minor league baseball player stats via text. Reply YES to subscribe or NO to decline. Msg & data rates may apply. Reply STOP anytime to cancel.
4. They reply **YES** — consent is recorded and alerts begin
5. They reply **NO** — no alerts are sent

### How opt-out works

- Every alert message ends with: `Reply STOP to unsubscribe`
- Replying **STOP** to any message immediately unsubscribes at both the carrier level (handled by Twilio) and in the local consent log
- Replying **YES** after a STOP re-subscribes

### Consent tracking

Consent status is stored in `consent.json` (excluded from git). The monitor checks consent before sending — recipients who haven't opted in are skipped. Check status anytime:
```bash
python send_optin.py --status
```

### Webhook (for reply handling on VPS)

The `webhook.py` Flask server handles incoming YES/NO/STOP replies. On your VPS, it runs alongside the monitor as a separate service. Configure your Twilio number's messaging webhook to point to `http://YOUR_VPS_IP:5000/sms`.

## Setup

### Requirements

- Python 3.9+
- A [Twilio](https://www.twilio.com) account (free trial works)
- A VPS for 24/7 operation ($5-6/month — DigitalOcean, Hetzner, Vultr, etc.)

### Install

```bash
git clone https://github.com/YOUR_USERNAME/milb-alerts.git
cd milb-alerts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure

```bash
cp config.example.json config.json
```

Edit `config.json` with your Twilio credentials and recipient info.

### Find Player IDs

```bash
python manage.py search "Roman Anthony"
python manage.py search --id 701328
python manage.py search --roster "Padres" --filter "Salas"
python manage.py search --url "https://www.milb.com/player/name-123456"
```

### Manage Watchlists

```bash
python manage.py add-person "Matt" "+13105551234"
python manage.py add --id 701328 --to Matt
python manage.py add --id 687765 --to Matt
python manage.py show Matt
python manage.py remove --id 701328 --from Matt
```

### Test

```bash
# Formatting test (no network needed)
python test_mock.py

# Real games from a specific date
python test_run.py --date 2026-03-07 --all

# Live monitor in console mode (prints to terminal, no SMS)
python monitor.py --console
```

### Run

```bash
# Send opt-in requests first
python send_optin.py all

# Start the monitor
python monitor.py
```

### Deploy to VPS

```bash
scp -r milb-alerts/ root@YOUR_SERVER_IP:/root/milb-alerts/
ssh root@YOUR_SERVER_IP
cd /root/milb-alerts
bash setup.sh
```

## Project Structure

```
milb-alerts/
├── monitor.py           Main polling loop (runs 24/7)
├── api.py               MLB Stats API interactions
├── formatter.py          Stats → SMS text formatting
├── notifier.py           Twilio SMS / console output
├── manage.py             CLI for managing players and contacts
├── player_search.py      Player ID lookup utility
├── consent.py            SMS opt-in/opt-out tracking
├── webhook.py            Twilio webhook for incoming replies
├── send_optin.py         Send opt-in requests to recipients
├── test_mock.py          Offline formatting tests
├── test_run.py           Test with real past games
├── config.example.json   Config template (copy to config.json)
├── requirements.txt      Python dependencies
├── setup.sh              VPS deployment script
├── milb-alerts.service   systemd service (monitor)
├── milb-webhook.service  systemd service (webhook)
├── TERMS.md              Terms of Service
└── PRIVACY.md            Privacy Policy
```

## Sport IDs

| ID | Level |
|----|-------|
| 1  | MLB / Spring Training |
| 11 | Triple-A (AAA) |
| 12 | Double-A (AA) |
| 13 | High-A (A+) |
| 14 | Single-A (A) |

Set which levels to monitor in `config.json` → `sport_ids`.

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by Major League Baseball, Minor League Baseball, or any MLB/MiLB team. Player statistics are sourced from MLB's publicly available Stats API. Use of MLB data is subject to [MLB's terms](http://gdx.mlb.com/components/copyright.txt).

## License

MIT — see [LICENSE](LICENSE)
