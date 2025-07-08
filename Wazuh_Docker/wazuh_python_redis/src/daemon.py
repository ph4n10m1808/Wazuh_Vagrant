import time
import os
import signal
import json
import redis
from config import POLL_INTERVAL, LAST_ALERT_FILE, REDIS
from utils import get_alerts

running = True

# Khởi tạo Redis 1 lần duy nhất
r = redis.Redis(
    host=REDIS["host"],
    port=REDIS["port"],
    db=REDIS["db"],
    password=REDIS.get("password")
)

def signal_handler(sig, frame):
    global running
    print("Stopping daemon...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def load_last_timestamp():
    if os.path.exists(LAST_ALERT_FILE):
        with open(LAST_ALERT_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_last_timestamp(timestamp):
    with open(LAST_ALERT_FILE, 'w') as f:
        f.write(timestamp)

def push_alert(alert):
    try:
        r.rpush(REDIS["alert_queue"], json.dumps(alert))
        print(f"[Pushed] {alert['@timestamp']} - {alert.get('rule', {}).get('description', 'No description')}")
    except Exception as e:
        print(f"[Redis Error] {e}")

def main():
    last_ts = load_last_timestamp()

    while running:
        try:
            alerts = get_alerts(from_timestamp=last_ts)
            if alerts:
                for alert in alerts:
                    push_alert(alert)
                last_ts = alerts[-1]['@timestamp']
                save_last_timestamp(last_ts)
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"[Error] {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    print("Starting Wazuh → Redis daemon (RPUSH)...")
    main()
