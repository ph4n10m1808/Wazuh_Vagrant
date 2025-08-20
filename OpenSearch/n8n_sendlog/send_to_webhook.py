import requests
import time
import json
import os
from config import WEBHOOK_URL

MAX_DURATION = 30  # Giới hạn thời gian gửi (giây)
DELAY_BETWEEN_SENDS = 5  # Thời gian giữa các lần gửi (giây)
UNSENT_FILE = "unsent_logs.txt"

def send_logs_to_webhook(logs):
    start_time = time.time()
    count = 0
    unsent_logs = []

    for i, item in enumerate(logs, 1):
        elapsed_time = time.time() - start_time
        if elapsed_time > MAX_DURATION:
            print(f"[!] Vượt quá {MAX_DURATION} giây. Dừng gửi và lưu log còn lại vào file.")
            unsent_logs.extend(logs[i-1:])
            break

        try:
            response = requests.post(WEBHOOK_URL, json=item)
            print(f"[{count+1}] Gửi: {item.get('rule.description', 'No Description')} | Status: {response.status_code}")
            count += 1
        except Exception as e:
            print(f"[!] Lỗi khi gửi object {i}: {e}")
            unsent_logs.append(item)

        time.sleep(DELAY_BETWEEN_SENDS)

    if unsent_logs:
        save_unsent_logs(unsent_logs)

    print(f"\n✅ Tổng cộng đã gửi {count} object.")

def save_unsent_logs(logs):
    with open(UNSENT_FILE, "a", encoding="utf-8") as f:
        for log in logs:
            f.write(json.dumps(log) + "\n")
    print(f"[⚠] Đã lưu {len(logs)} log chưa gửi vào {UNSENT_FILE}")

def load_unsent_logs():
    if not os.path.exists(UNSENT_FILE):
        return []

    logs = []
    with open(UNSENT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                logs.append(json.loads(line.strip()))
            except Exception as e:
                print(f"[!] Bỏ qua 1 dòng không hợp lệ: {e}")

    # Xóa file sau khi tải
    os.remove(UNSENT_FILE)
    return logs

def main():
    # 1. Đọc log mới từ file hoặc nguồn nào đó
    with open("log.json", "r", encoding="utf-8") as f:
        logs = json.load(f)

    print(f"[+] Đang gửi {len(logs)} log mới...")
    send_logs_to_webhook(logs)

    # 2. Gửi lại các log chưa gửi từ lần trước (nếu có)
    unsent = load_unsent_logs()
    if unsent:
        print(f"[+] Đang gửi lại {len(unsent)} log từ {UNSENT_FILE}...")
        send_logs_to_webhook(unsent)

if __name__ == "__main__":
    main()
