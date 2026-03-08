FROM python:3.9-slim

# ติดตั้ง dependencies สำหรับ SQL Server Driver
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "80"]