# src/main.py

from redis_client import connect_redis
from opensearch_client import connect_opensearch
from normalizer import process_alert
from config import ALERT_QUEUE, OS_INDEX
from datetime import datetime

def main():
    redis_client = connect_redis()
    os_client = connect_opensearch()

    print("[*] Listening for Wazuh alerts...")

    while True:
        alert_raw = redis_client.lpop(ALERT_QUEUE)
        if not alert_raw:
            continue

        alert = process_alert(alert_raw)
        if not alert:
            continue

        # Generate dynamic index name based on current date
        index_name = f"{OS_INDEX}-{datetime.utcnow().strftime('%Y.%m.%d')}"
        os_client.index(index=index_name, body=alert)
        print(f"[+] Normalized alert: {alert['uuid']}")

if __name__ == "__main__":
    main()
