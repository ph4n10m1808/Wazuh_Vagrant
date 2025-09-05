import os
import json
import time
import uuid
import requests
from datetime import datetime, timedelta
from opensearchpy import OpenSearch

# --- Config từ ENV ---
OPENSEARCH_HOST = "https://opensearch-node1:9201"
OPENSEARCH_USER = "admin"
OPENSEARCH_PASS = "Administrator@123"
INDEX_NAME = "normalized-alerts*"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1"
MODEL = "llama-3.1-8b-instant"

LOG_FILE = "/data/logs_batch.json"
BATCH_INPUT_FILE = "/data/input.jsonl"
OUTPUT_FILE = "/data/output/output.jsonl"

# --- Kết nối OpenSearch ---
client = OpenSearch(
    hosts=[OPENSEARCH_HOST],
    http_auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
    verify_certs=False
)

def collect_logs():
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=1)

    query = {
        "query": {
            "range": {
                "@timestamp": {
                    "gte": start_time.isoformat(),
                    "lte": end_time.isoformat()
                }
            }
        },
        "sort": [{"@timestamp": {"order": "asc"}}]
    }

    print(f"[DEBUG] Querying OpenSearch with: {json.dumps(query, indent=2)}")
    response = client.search(index=INDEX_NAME, body=query)
    logs = [hit["_source"] for hit in response["hits"]["hits"]]

    print(f"[DEBUG] Raw response hits: {len(response['hits']['hits'])}")
    if logs:
        print(f"[DEBUG] First log sample: {json.dumps(logs[0], indent=2)}")

    os.makedirs("/data", exist_ok=True)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

    print(f"[INFO] Collected {len(logs)} logs from OpenSearch")
    return logs

def prepare_batch_file(logs):
    """Viết logs sang file JSONL để upload lên Groq batch API"""
    system_prompt = """Bạn là nhà phân tích SOC Tier 1. Dựa trên log đầu vào (cung cấp sau), hãy phân tích và trả về kết quả duy nhất dưới dạng JSON thuần đúng định dạng bên dưới. Không được thêm mô tả, markdown, tiêu đề, hay bất kỳ nội dung nào khác ngoài JSON.

Yêu cầu xử lý:

Phân loại mức cảnh báo theo mức độ nghiêm trọng: CRITICAL, HIGH, MEDIUM, LOW, INFO

Nếu thiếu thông tin, điền "unknown" hoặc null

Không được bịa ra thông tin nếu log không cung cấp

Trả lời duy nhất 1 lần bằng JSON hợp lệ

Mẫu định dạng JSON đầu ra:
```json
{
  "alert_level": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
  "event_name": "Tên sự kiện hoặc tóm tắt",
  "detection_time": "Thời gian phát hiện (UTC hoặc local time)",
  "affected_host": "Tên máy chủ hoặc thiết bị bị ảnh hưởng",
  "affected_ip": "Địa chỉ IP của máy bị ảnh hưởng",
  "user_involved": "Tài khoản người dùng liên quan (nếu có)",
  "event_description": "Mô tả ngắn gọn về sự kiện",
  "short_analysis": "Phân tích ngắn gọn nguyên nhân và tác động",
  "potential_risks": "Các rủi ro tiềm ẩn nếu không xử lý",
  "immediate_actions": "Hành động cần thực hiện ngay để giảm thiểu rủi ro",
  "playbook_id": "Mã hoặc tên playbook xử lý liên quan",
  "incident_status": "open | in_progress | resolved | false_positive",
  "rule_changed": "True | False",
  "Rule Changed": "Thông tin mô tả nếu rule đã bị sửa"
}
```
"""
    print(f"[DEBUG] Preparing batch file with {len(logs)} logs")
    with open(BATCH_INPUT_FILE, "w", encoding="utf-8") as f:
        for i, log in enumerate(logs, start=1):
            entry = {
                "custom_id": f"log-{i}-{uuid.uuid4().hex[:8]}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(log, ensure_ascii=False)}
                    ],
                    "temperature": 0.0
                }
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            if i == 1:  # chỉ in debug cho log đầu tiên
                print(f"[DEBUG] First batch entry: {json.dumps(entry, indent=2)}")

    print(f"[INFO] ✅ Batch input file saved: {BATCH_INPUT_FILE}")

def upload_file():
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"file": open(BATCH_INPUT_FILE, "rb")}
    data = {"purpose": "batch"}
    print(f"[DEBUG] Uploading batch file {BATCH_INPUT_FILE} to Groq API...")
    r = requests.post(f"{GROQ_URL}/files", headers=headers, files=files, data=data)
    print(f"[DEBUG] Upload response: {r.status_code} {r.text}")
    r.raise_for_status()
    file_id = r.json()["id"]
    print(f"[INFO] ✅ File uploaded: {file_id}")
    try:
        os.remove(BATCH_INPUT_FILE)
        print(f"[DEBUG] 🗑️ Deleted {BATCH_INPUT_FILE} after upload")
    except Exception as e:
        print(f"[WARN] Could not delete {BATCH_INPUT_FILE}: {e}")
    return file_id

def create_batch(file_id):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "input_file_id": file_id,
        "endpoint": "/v1/chat/completions",
        "completion_window": "24h"
    }
    print(f"[DEBUG] Creating batch with payload: {json.dumps(payload, indent=2)}")
    r = requests.post(f"{GROQ_URL}/batches", headers=headers, json=payload)
    print(f"[DEBUG] Create batch response: {r.status_code} {r.text}")
    r.raise_for_status()
    batch_id = r.json()["id"]
    print(f"[INFO] ✅ Batch created: {batch_id}")
    return batch_id

def check_batch_status(batch_id):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    url = f"{GROQ_URL}/batches/{batch_id}"
    r = requests.get(url, headers=headers)
    print(f"[DEBUG] Check status response: {r.status_code} {r.text}")
    r.raise_for_status()
    return r.json()

def download_output_file(file_id, save_path=OUTPUT_FILE):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    url = f"{GROQ_URL}/files/{file_id}/content"
    print(f"[DEBUG] Downloading output file {file_id} from {url}")
    r = requests.get(url, headers=headers)
    print(f"[DEBUG] Download response status: {r.status_code}")
    r.raise_for_status()
    with open(save_path, "ab") as f:
        f.write(r.content)
        f.write(b"\n")  # đảm bảo mỗi lần ghi là một dòng mới
    print(f"[INFO] ✅ Output saved: {save_path}")

def wait_and_download(batch_id):
    print(f"[INFO] ⏳ Waiting for batch {batch_id} to finish...")
    while True:
        status = check_batch_status(batch_id)
        state = status.get("status")
        print(f"[DEBUG] Batch {batch_id} status: {state}")
        if state in ["completed", "failed", "cancelled"]:
            break
        time.sleep(20)

    if state == "completed":
        output_file_id = status.get("output_file_id")
        if output_file_id:
            print(f"[DEBUG] Output file id: {output_file_id}")
            download_output_file(output_file_id)
        else:
            print("[ERROR] No output_file_id found in batch result")
    else:
        print(f"[ERROR] Batch ended with status: {state}")

if __name__ == "__main__":
    while True:
        logs = collect_logs()
        if logs:
            prepare_batch_file(logs)
            file_id = upload_file()
            batch_id = create_batch(file_id)
            wait_and_download(batch_id)
        else:
            print("[DEBUG] No logs collected in this cycle")
        time.sleep(60)
