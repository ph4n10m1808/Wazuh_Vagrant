# src/config/config.py

REDIS_CONF = {
    "host": "wazuh.indexer",
    "port": 6379,
    "db": 0,
    "password": "eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81"
}

ALERT_QUEUE = "wazuh:alerts"

OS_CONF = {
    "hosts": [{"host": "opensearch-node1", "port": 9200}],
    "http_auth": ("admin", "Administrator@123"),
    "use_ssl": True,
    "verify_certs": False,
}

OS_INDEX = "normalized-alerts"
