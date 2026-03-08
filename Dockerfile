FROM python:3.9-slim

# ติดตั้งเครื่องมือที่จำเป็นสำหรับ pyodbc และ SQL Server
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    g++ \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ก๊อปปี้ไฟล์และติดตั้ง Library
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ก๊อปปี้โค้ดทั้งหมด
COPY . .

# สั่งรันแอป
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]