FROM python:3.10-slim
# Set the working directory
WORKDIR /app
# Copy the requirements file into the container
COPY ./src /app
# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]

