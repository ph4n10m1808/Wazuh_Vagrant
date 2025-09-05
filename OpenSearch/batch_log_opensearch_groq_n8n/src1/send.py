import requests
import json
import time

URL = "https://hot-newt-externally.ngrok-free.app/webhook/ad8c5b20-c489-45e0-b03f-b342ae91fedc"
FILE = "./output/output.jsonl"

def process_file():
    while True:
        try:
            # Đọc tất cả dòng
            with open(FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if not lines:
                time.sleep(1)
                continue

            # Lấy dòng đầu tiên
            first_line = lines[0].strip()
            if not first_line:
                # Nếu dòng trống thì bỏ qua
                with open(FILE, "w", encoding="utf-8") as f:
                    f.writelines(lines[1:])
                continue

            try:
                body = json.loads(first_line)
            except json.JSONDecodeError:
                # print("⚠️ Không parse được JSON:", first_line)
                # Bỏ qua dòng lỗi
                with open(FILE, "w", encoding="utf-8") as f:
                    f.writelines(lines[1:])
                continue

            # Gửi POST
            resp = requests.post(URL, json=body)
            if resp.status_code == 200:
                # print("✅ Sent:", body)
                # Xóa dòng đã xử lý
                with open(FILE, "w", encoding="utf-8") as f:
                    f.writelines(lines[1:])
                # Rate limit: 20 messages / minute => 1 msg mỗi 3s
                time.sleep(3)
            else:
                # print(f"❌ Lỗi gửi ({resp.status_code}):", resp.text)
                time.sleep(1)

        except Exception as e:
            print("⚠️ Error:", e)
            time.sleep(1)

if __name__ == "__main__":
    process_file()
