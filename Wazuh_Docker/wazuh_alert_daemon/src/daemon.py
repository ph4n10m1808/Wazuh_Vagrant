import time
import os
import signal
import json
from config import POLL_INTERVAL, LAST_ALERT_FILE, ALERT_LOG_FILE
from utils import get_alerts
from datetime import datetime

running = True

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

def log_alert(alert):
    try:
        with open(ALERT_LOG_FILE, 'a') as f:
            f.write(json.dumps(alert) + '\n')
        print(f"[Saved] {alert['@timestamp']} - {alert.get('rule', {}).get('description', 'No description')}")
    except Exception as e:
        print(f"[Log Error] {e}")

def main():
    # last_ts = load_last_timestamp()

    # while running:
    #     try:
    #         alerts = get_alerts(from_timestamp=last_ts)
    #         if alerts:
    #             for alert in alerts:
    #                 log_alert(alert)
    #             last_ts = alerts[-1]['@timestamp']
    #             save_last_timestamp(last_ts)
    #         time.sleep(POLL_INTERVAL)
    #     except Exception as e:
    #         print(f"Error fetching alerts: {e}")
    #         time.sleep(POLL_INTERVAL)
    # Check and rotate or delete old alerts.txt
    if os.path.exists(ALERT_LOG_FILE):
        # Option 1: Rename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{ALERT_LOG_FILE.rstrip('.txt')}_{timestamp}.txt"
        os.rename(ALERT_LOG_FILE, new_name)
        print(f"Renamed old {ALERT_LOG_FILE} to {new_name}")

        # Option 2: Or delete (uncomment this to use instead)
        # os.remove(ALERT_LOG_FILE)
        # print(f"Deleted existing {ALERT_LOG_FILE}")

    last_ts = load_last_timestamp()

    while running:
        try:
            alerts = get_alerts(from_timestamp=last_ts)
            if alerts:
                for alert in alerts:
                    log_alert(alert)
                last_ts = alerts[-1]['@timestamp']
                save_last_timestamp(last_ts)
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    print("Starting Wazuh Indexer Alert Logger...")
    main()
    from datetime import datetime


