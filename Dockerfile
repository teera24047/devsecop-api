FROM python:3.9-slim

# 1. ติดตั้งเครื่องมือที่จำเป็น (ใช้กุญแจแบบ gpg แทน apt-key)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    g++ \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. เพิ่ม Microsoft Repo ด้วยวิธีใหม่ (ไม่ใช้ apt-key)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list

# 3. ติดตั้ง SQL Driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

WORKDIR /app

# 4. ติดตั้ง Python Packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. ก๊อปปี้โค้ด
COPY . .

# 6. สั่งรัน (ถ้าไฟล์ชื่อ app.py ให้แก้เป็น app:app นะครับ)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]