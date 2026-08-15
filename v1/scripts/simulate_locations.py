#!/usr/bin/env python3
"""
simulate_locations.py

Nudges the demo cards' GPS coordinates every few seconds so the dashboard's
"live" map has something to actually watch move. Writes directly to the
`locations` table via PyMySQL (no API/auth token needed), so it works even
before the Flask app is running.

Usage:
    python api/v1/scripts/simulate_locations.py
    python api/v1/scripts/simulate_locations.py --interval 5 --steps 200

Requires the demo data from api/v1/database/seed-demo.sql to already be
loaded (it only moves cards with IMEI numbers starting with '86800001').
"""

import argparse
import random
import time

import pymysql

DB_CONFIG = dict(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='toor',
    database='gps_tracker',
    autocommit=True,
)

DEMO_IMEI_PREFIX = '86800001'

# Roughly +/-30-60m per tick, enough to visibly walk across a city block.
MAX_STEP_DEGREES = 0.0006


def fetch_demo_cards(conn):
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(
            "SELECT id, name FROM cards WHERE imei_number LIKE %s",
            (f'{DEMO_IMEI_PREFIX}%',),
        )
        return cur.fetchall()


def latest_location(conn, card_id):
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        cur.execute(
            "SELECT lat, lng, battery FROM locations "
            "WHERE card_id = %s ORDER BY id DESC LIMIT 1",
            (card_id,),
        )
        return cur.fetchone()


def insert_location(conn, card_id, lat, lng, speed, battery, sos):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO locations (card_id, lat, lng, speed, battery, sos_button_pressed) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (card_id, lat, lng, speed, battery, sos),
        )


def step(conn, card, sos_chance):
    current = latest_location(conn, card['id'])
    if current is None:
        print(f"  skip {card['name']}: no starting fix (run seed-demo.sql first)")
        return

    lat = float(current['lat']) + random.uniform(-MAX_STEP_DEGREES, MAX_STEP_DEGREES)
    lng = float(current['lng']) + random.uniform(-MAX_STEP_DEGREES, MAX_STEP_DEGREES)
    speed = round(random.uniform(0, 40), 1)

    battery = current['battery'] if current['battery'] is not None else 100
    # Battery drains slowly and occasionally gets "recharged" to keep the demo alive.
    battery = max(1, battery - random.choice([0, 0, 1])) if battery > 15 else 100

    sos = 1 if random.random() < sos_chance else 0

    insert_location(conn, card['id'], lat, lng, speed, battery, sos)
    flag = ' [SOS]' if sos else ''
    print(f"  {card['name']}: {lat:.5f}, {lng:.5f}  speed={speed}km/h battery={battery}%{flag}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interval', type=float, default=5.0, help='Seconds between ticks (default: 5)')
    parser.add_argument('--steps', type=int, default=0, help='Number of ticks to run (default: run forever)')
    parser.add_argument('--sos-chance', type=float, default=0.0, help='Probability (0-1) any card triggers SOS per tick')
    args = parser.parse_args()

    conn = pymysql.connect(**DB_CONFIG)
    try:
        cards = fetch_demo_cards(conn)
        if not cards:
            print(f"No demo cards found (IMEI starting with '{DEMO_IMEI_PREFIX}'). "
                  f"Run api/v1/database/seed-demo.sql first.")
            return

        print(f"Simulating movement for {len(cards)} card(s) every {args.interval}s. Ctrl+C to stop.")
        tick = 0
        while args.steps == 0 or tick < args.steps:
            tick += 1
            print(f"tick {tick}:")
            for card in cards:
                step(conn, card, args.sos_chance)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
