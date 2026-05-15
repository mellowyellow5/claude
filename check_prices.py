#!/usr/bin/env python3
import json
import os
import subprocess
import sys
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

    # raw is a list of objects keyed by itad_id
    price_map = {item["id"]: item for item in raw}

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

        print(f"  [{name}] Current lowest: {price:.2f} SEK (threshold: {threshold} SEK)")

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
