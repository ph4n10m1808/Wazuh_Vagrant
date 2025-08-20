from opensearchpy import OpenSearch
from datetime import datetime, timedelta
import time
from send_to_webhook import send_logs_to_webhook

# Cấu hình kết nối OpenSearch
client = OpenSearch(
    hosts=[{'host': 'opensearch-node1', 'port': 9200}],
    http_auth=('admin', 'Administrator@123'),  # Chỉnh sửa nếu cần
    use_ssl=True, verify_certs=False,  # Dùng self-signed cert thì giữ False
)

INDEX_PATTERN = "normalized-alerts-*"

def iso_now_minus(seconds):
    return (datetime.utcnow() - timedelta(seconds=seconds)).isoformat() + "Z"

def get_logs():
    now = datetime.utcnow().isoformat() + "Z"
    start_time = iso_now_minus(30)

    body = {
        "size": 1000,
        "sort": [{"@timestamp": "asc"}],
        "query": {
            "range": {
                "@timestamp": {
                    "gte": start_time,
                    "lte": now
                }
            }
        }
    }

    all_logs = []
    last_sort = None

    while True:
        if last_sort:
            body["search_after"] = last_sort

        response = client.search(index=INDEX_PATTERN, body=body)
        hits = response["hits"]["hits"]

        if not hits:
            break

        all_logs.extend([hit["_source"] for hit in hits])
        last_sort = hits[-1]["sort"]

    return all_logs

if __name__ == "__main__":
    while True:
        print("🔍 Đang truy vấn log mới...")
        logs = get_logs()

        if logs:
            print(f"📦 Tìm thấy {len(logs)} log mới. Gửi đến webhook...")
            send_logs_to_webhook(logs)
        else:
            print("⏳ Không có log nào mới.")

        time.sleep(30)
