WAZUH_INDEXER = {
    "host": "https://wazuh.indexer",  # hoặc https://127.0.0.1
    "port": 9200,
    "index": "wazuh-alerts-4.x-*",
    "user": "admin",
    "password": "SecretPassword",
    "verify_ssl": False
}

REDIS = {
    "host": "wazuh.indexer",
    "port": 6379,
    "db": 0,
    "alert_queue": "wazuh:alerts",
    "password": "eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81"
}

POLL_INTERVAL = 1  # giây
LAST_ALERT_FILE = "last_alert_timestamp.txt"
