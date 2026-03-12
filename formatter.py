"""
formatter.py — Format player stats into SMS-ready text messages.

Hitter format:
  Name Level/ORG @ OPP
  H-AB | 2B, R, BB          (only non-zero, no count if 1)

Pitcher format:
  Name Level/ORG vs OPP
  (W) 3.0 IP, 2 H, 0 R, 0 ER, 3 K, 0 BB, 0 HR
"""

OPT_OUT_FOOTER = "\nReply STOP to unsubscribe"


def format_game_message(game: dict, player_stats: list[dict]) -> str:
    lines = []

    for i, ps in enumerate(player_stats):
        if i > 0:
            lines.append("")

        name = ps["name"]
        side = ps.get("side", "away")
        level = game.get("level", "MiLB")

        if side == "away":
            team_abbr = game.get("away_abbr", "???")
            opp_abbr = game.get("home_abbr", "???")
            direction = "@"
        else:
            team_abbr = game.get("home_abbr", "???")
            opp_abbr = game.get("away_abbr", "???")
            direction = "vs"

        header = f"{name} {level}/{team_abbr} {direction} {opp_abbr}"

        if "batting" in ps:
            lines.append(header)
            lines.append(_format_batting(ps["batting"]))

        if "pitching" in ps:
            if "batting" in ps:
                lines.append(header + " (P)")
            else:
                lines.append(header)
            lines.append(_format_pitching(ps["pitching"]))

    return "\n".join(lines) + OPT_OUT_FOOTER


def _format_batting(b: dict) -> str:
    base = f"{b['h']}-{b['ab']}"
    extras = []

    def _add(val, label):
        if val == 1:
            extras.append(label)
        elif val > 1:
            extras.append(f"{val} {label}")

    _add(b["r"], "R")
    _add(b["doubles"], "2B")
    _add(b["triples"], "3B")
    _add(b["hr"], "HR")
    _add(b["rbi"], "RBI")
    _add(b["k"], "K")
    _add(b["bb"], "BB")
    _add(b["sb"], "SB")

    if extras:
        return f"{base} | {', '.join(extras)}"
    return base


def _format_pitching(p: dict) -> str:
    decision = p.get("decision")
    prefix = f"({decision}) " if decision else ""

    parts = [
        f"{p['ip']} IP",
        f"{p['h']} H",
        f"{p['r']} R",
        f"{p['er']} ER",
        f"{p['k']} K",
        f"{p['bb']} BB",
        f"{p['hr']} HR",
    ]

    return prefix + ", ".join(parts)
