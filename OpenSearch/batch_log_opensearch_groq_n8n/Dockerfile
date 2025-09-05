FROM python:3.10-slim

WORKDIR /data

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app.py .  

# Thư mục lưu log file
VOLUME ["/data"]

CMD ["python", "app.py"]
