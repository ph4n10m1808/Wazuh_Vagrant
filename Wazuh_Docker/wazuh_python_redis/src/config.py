WAZUH_INDEXER = {
    "host": "https://wazuh.indexer",  # URl Wazuh Indexer
    "port": 9200, # Port Wazuh Indexer
    "index": "wazuh-alerts-4.x-*", # Index Wazuh for alerts
    "user": "admin", # Username for Wazuh Indexer 
    "password": "SecretPassword", # Password for Wazuh Indexer
    "verify_ssl": False # Verify SSL certificate
}

REDIS = {
    "host": "wazuh.indexer", # Host Redis
    "port": 6379, # Port Redis
    "db": 0,  # Database
    "alert_queue": "wazuh:alerts", # Redis queue for alerts
    "password": "eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81" # Password for Redis
}

POLL_INTERVAL = 0.5  # Interval in seconds to poll for new alerts
LAST_ALERT_FILE = "last_alert_timestamp.txt" # File to store the timestamp of the last processed alert
