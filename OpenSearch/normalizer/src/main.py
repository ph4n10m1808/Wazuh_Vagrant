# import redis
# import json
# import uuid
# import flatdict
# from opensearchpy import OpenSearch

# # Cấu hình Redis và OpenSearch
# REDIS_CONF = {
#     "host": "wazuh.indexer",
#     "port": 6379,
#     "db": 0,
#     "password": "eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81"
# }
# ALERT_QUEUE = "wazuh:alerts"

# OS_CONF = {
#     "hosts": [{"host": "localhost", "port": 9200}],
#     "http_auth": ("admin", "Administrator@123"),
#     "use_ssl": True,
#     "verify_certs": False,
# }
# OS_INDEX = "normalized-alerts"

# # Các trường cần loại bỏ khi chuẩn hóa
# FIELDS_TO_DROP = [
#     "manager", "decoder", "input", "full_log", "previous_log", "previous_output", "id",
#     "rule.firedtimes", "rule.mail", "rule.pci_dss", "rule.hipaa", "rule.nist_800_53",
#     "rule.tsc", "rule.gpg13", "rule.gdpr"
# ]

# # Kết nối Redis
# def connect_redis():
#     return redis.StrictRedis(
#         host=REDIS_CONF["host"],
#         port=REDIS_CONF["port"],
#         db=REDIS_CONF["db"],
#         password=REDIS_CONF["password"],
#         decode_responses=True
#     )

# # Kết nối OpenSearch
# def connect_opensearch():
#     return OpenSearch(**OS_CONF)

# # Chuẩn hóa alert: flatten, gán UUID, phân loại severity
# def normalize_alert(alert_data: dict) -> dict:
#     flattened = dict(flatdict.FlatDict(alert_data, delimiter="."))

#     # Xoá các trường không cần thiết
#     for field in FIELDS_TO_DROP:
#         flattened.pop(field, None)

#     # Gán UUID
#     flattened["uuid"] = str(uuid.uuid4())

#     # Gắn timestamp (nếu thiếu)
#     flattened["timestamp"] = alert_data.get("timestamp", "now")

#     # Phân loại severity dựa trên rule.level
#     level = flattened.get("rule.level", 0)
#     try:
#         level = int(level)
#     except ValueError:
#         level = 0

#     if level >= 12:
#         severity = "critical"
#     elif level >= 7:
#         severity = "high"
#     elif level >= 4:
#         severity = "medium"
#     else:
#         severity = "low"

#     flattened["severity"] = severity

#     return flattened

# # Xử lý alert từ Redis
# def process_alert(alert_json):
#     try:
#         alert_data = json.loads(alert_json)
#     except json.JSONDecodeError:
#         return None
#     return normalize_alert(alert_data)

# # Chương trình chính
# def main():
#     redis_client = connect_redis()
#     os_client = connect_opensearch()

#     print("[*] Listening for Wazuh alerts...")

#     while True:
#         alert_raw = redis_client.lpop(ALERT_QUEUE)
#         if not alert_raw:
#             continue

#         alert = process_alert(alert_raw)
#         if not alert:
#             continue

#         os_client.index(index=OS_INDEX, body=alert)
#         print(f"[+] Normalized alert: {alert['uuid']} - Severity: {alert['severity']}")

# if __name__ == "__main__":
#     main()
# src/python/main.py

from redis_client import connect_redis
from opensearch_client import connect_opensearch
from normalizer import process_alert
from config import ALERT_QUEUE, OS_INDEX

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

        os_client.index(index=OS_INDEX, body=alert)
        print(f"[+] Normalized alert: {alert['uuid']} - Severity: {alert['severity']}")

if __name__ == "__main__":
    main()

