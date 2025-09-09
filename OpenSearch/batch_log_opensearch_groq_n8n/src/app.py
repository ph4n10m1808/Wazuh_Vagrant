import os
import json
import time
import uuid
import requests
from datetime import datetime, timedelta
from opensearchpy import OpenSearch

# --- Config từ ENV ---
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST")
OPENSEARCH_USER = os.getenv("OPENSEARCH_USER")
OPENSEARCH_PASS = os.getenv("OPENSEARCH_PASS")
INDEX_NAME = os.getenv("INDEX_NAME")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = os.getenv("GROQ_URL")
MODEL = os.getenv("MODEL")

BATCH_INPUT_FILE = os.getenv("BATCH_INPUT_FILE")
OUTPUT_FILE = os.getenv("OUTPUT_FILE")

# --- Kết nối OpenSearch ---
client = OpenSearch(
    hosts=[OPENSEARCH_HOST],
    http_auth=(OPENSEARCH_USER, OPENSEARCH_PASS),
    verify_certs=False
)

last_timestamp = None

def collect_logs():
    global last_timestamp
    end_time = datetime.utcnow()
    if last_timestamp is None:
        start_time = end_time - timedelta(seconds=30)
    else:
        start_time = last_timestamp
    
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

    response = client.search(index=INDEX_NAME, body=query,size=1000)
    logs = [hit["_source"] for hit in response["hits"]["hits"]]
    if logs:
        last_timestamp = datetime.fromisoformat(logs[-1]["@timestamp"].replace("Z", "+00:00"))

    return logs

def prepare_batch_file(logs):
    """Viết logs sang file JSONL để upload lên Groq batch API"""
    system_prompt = """You are a Tier 1 SOC Analyst. Based on the provided input logs (to be given later), analyze and return the result strictly in JSON format as specified below. Do not include any descriptions, markdown, headers, or any content outside of valid JSON.

Processing requirements:

- Classify the alert severity level as one of: CRITICAL, HIGH, MEDIUM, LOW, INFO  
- If any information is missing, use "unknown" or null  
- Do not fabricate details if logs do not provide them  
- Respond exactly once with valid JSON only
Mandatory output JSON schema:

```json
{
  "alert_level": "CRITICAL | HIGH | MEDIUM | LOW | INFO",
  "event_name": "Name of the event or summary",
  "detection_time": "Detection timestamp (UTC or local time)",
  "affected_host": "Hostname or device impacted",
  "affected_ip": "IP address of the affected host",
  "user_involved": "Relevant user account (if any)",
  "event_description": "Brief description of the event",
  "short_analysis": "Short analysis of cause and potential impact",
  "potential_risks": "Possible risks if left unremediated",
  "immediate_actions": "Immediate actions required to mitigate risk",
  "playbook_id": "Identifier or name of applicable response playbook",
  "incident_status": "open | in_progress | resolved | false_positive",
  "rule_changed": "True | False",
  "Rule Changed": "Description if the detection rule was modified"
}
```
"""

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

def upload_file():
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"file": open(BATCH_INPUT_FILE, "rb")}
    data = {"purpose": "batch"}
    r = requests.post(f"{GROQ_URL}/files", headers=headers, files=files, data=data)
    r.raise_for_status()
    file_id = r.json()["id"]
    try:
        os.remove(BATCH_INPUT_FILE)
    except Exception as e:
        print({e})
    return file_id

def create_batch(file_id):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "input_file_id": file_id,
        "endpoint": "/v1/chat/completions",
        "completion_window": "24h"
    }
    r = requests.post(f"{GROQ_URL}/batches", headers=headers, json=payload)
    r.raise_for_status()
    batch_id = r.json()["id"]
    return batch_id

def check_batch_status(batch_id):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    url = f"{GROQ_URL}/batches/{batch_id}"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def download_output_file(file_id, save_path=OUTPUT_FILE):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    url = f"{GROQ_URL}/files/{file_id}/content"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    with open(save_path, "ab") as f:
        f.write(r.content)
        f.close()

def wait_and_download(batch_id):
    while True:
        status = check_batch_status(batch_id)
        state = status.get("status")
        if state in ["completed", "failed", "cancelled"]:
            break
        time.sleep(2)

    if state == "completed":
        output_file_id = status.get("output_file_id")
        if output_file_id:
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
            print("No logs collected in this cycle")
        time.sleep(2)
