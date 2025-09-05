FROM python:3.10-slim

WORKDIR /data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY send.py .  

# Thư mục lưu log file
# VOLUME ["/data"]

CMD ["python", "send.py"]
