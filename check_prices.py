#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv

load_dotenv()

ITAD_API_KEY = os.getenv("ITAD_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

GAMES_FILE = Path(__file__).parent / "games.yaml"
STATE_FILE = Path(__file__).parent / "state.json"

ITAD_PRICES_URL = "https://api.isthereanydeal.com/games/prices/v3"
ITAD_HISTORY_URL = "https://api.isthereanydeal.com/games/history/v3"


def load_games():
    with open(GAMES_FILE) as f:
        return yaml.safe_load(f)


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_prices(itad_ids):
    """Fetch lowest current prices for a list of ITAD game IDs."""
    params = {
        "key": ITAD_API_KEY,
        "country": "SE",
        "shops": "",  # all shops
    }
    # The v3 endpoint takes game IDs as query params
    response = requests.post(
        ITAD_PRICES_URL,
        params=params,
        json=itad_ids,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def get_lowest_price_sek(price_data):
    """Return the lowest price in SEK from a game's price data, or None."""
    prices = price_data.get("deals", [])
    if not prices:
        return None
    return min(deal["price"]["amount"] for deal in prices)


def fetch_history(itad_ids, days=30):
    """Fetch price history for the last `days` days for a list of ITAD game IDs."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    params = {
        "key": ITAD_API_KEY,
        "country": "SE",
        "since": int(since.timestamp()),
    }
    response = requests.post(
        ITAD_HISTORY_URL,
        params=params,
        json=itad_ids,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def history_low(history_data, since_hours=None):
    """Return the lowest price from history entries, optionally limited to the last N hours."""
    cutoff = None
    if since_hours is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)

    low = None
    for entry in history_data:
        if cutoff is not None:
            ts = datetime.fromtimestamp(entry["timestamp"], tz=timezone.utc)
            if ts < cutoff:
                continue
        amount = entry["deal"]["price"]["amount"]
        if low is None or amount < low:
            low = amount
    return low


def notify_desktop(title, message):
    try:
        subprocess.run(
            ["notify-send", "--urgency=normal", title, message],
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"  Desktop notification failed: {e}", file=sys.stderr)


def notify_discord(game_name, price, threshold):
    if not DISCORD_WEBHOOK_URL:
        return
    payload = {
        "content": (
            f":rotating_light: **Price alert!**\n"
            f"**{game_name}** is now **{price:.2f} SEK** "
            f"(threshold: {threshold} SEK)\n"
            f"<https://isthereanydeal.com/search/?q={requests.utils.quote(game_name)}>"
        )
    }
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"  Discord notification failed: {e}", file=sys.stderr)


def main():
    if not ITAD_API_KEY:
        sys.exit("Error: ITAD_API_KEY is not set. Copy .env.example to .env and fill it in.")

    games = load_games()
    state = load_state()
    state_changed = False

    itad_ids = [g["itad_id"] for g in games]
    print(f"Checking prices for {len(games)} game(s)...")

    try:
        raw = fetch_prices(itad_ids)
    except requests.RequestException as e:
        sys.exit(f"Failed to fetch prices from ITAD: {e}")

    try:
        history_raw = fetch_history(itad_ids, days=30)
    except requests.RequestException as e:
        print(f"Warning: could not fetch price history: {e}", file=sys.stderr)
        history_raw = []

    price_map = {item["id"]: item for item in raw}
    history_map = {item["id"]: item.get("history", []) for item in history_raw}

    for game in games:
        gid = game["itad_id"]
        name = game["game"]
        threshold = game["threshold_sek"]

        data = price_map.get(gid)
        if data is None:
            print(f"  [{name}] No data returned — check the itad_id.")
            continue

        price = get_lowest_price_sek(data)
        if price is None:
            print(f"  [{name}] No deals found currently.")
            continue

        hist = history_map.get(gid, [])
        low_24h = history_low(hist, since_hours=24)
        low_30d = history_low(hist)

        print(f"  [{name}]")
        print(f"    Current:   {price:.2f} SEK")
        print(f"    24hr low:  {f'{low_24h:.2f} SEK' if low_24h is not None else 'n/a'}")
        print(f"    30day low: {f'{low_30d:.2f} SEK' if low_30d is not None else 'n/a'}")
        print(f"    Threshold: {threshold} SEK")

        was_alerted = state.get(gid, {}).get("alerted", False)

        if price < threshold:
            if not was_alerted:
                print(f"    -> BELOW threshold! Sending notifications.")
                notify_desktop(
                    "Game price alert",
                    f"{name} is {price:.2f} SEK (under {threshold} SEK)",
                )
                notify_discord(name, price, threshold)
                state[gid] = {"alerted": True, "last_price": price}
                state_changed = True
            else:
                print(f"    -> Still below threshold, already notified.")
        else:
            if was_alerted:
                # Price recovered — reset so we alert on the next drop
                state[gid] = {"alerted": False, "last_price": price}
                state_changed = True
            print(f"    -> Above threshold, no alert.")

    if state_changed:
        save_state(state)

    print("Done.")


if __name__ == "__main__":
    main()
