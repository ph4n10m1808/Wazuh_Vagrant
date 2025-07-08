WAZUH_INDEXER = {
    "host": "https://wazuh.indexer",  # or https://127.0.0.1
    "port": 9200,
    "index": "wazuh-alerts-4.x-*",
    "user": "admin",
    "password": "SecretPassword",
    "verify_ssl": False
}

POLL_INTERVAL = 0.5  # seconds
LAST_ALERT_FILE = "last_alert_timestamp.txt"
ALERT_LOG_FILE = "alerts.txt"
