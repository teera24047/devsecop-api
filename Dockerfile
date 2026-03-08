FROM python:3.9-slim

# 1. ติดตั้ง dependencies พื้นฐานที่จำเป็นสำหรับระบบ (เพิ่มปุ่มกดและตัวอ่าน repository)
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    g++ \
    unixodbc-dev \
    apt-transport-https \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 2. เพิ่ม Microsoft Key และ Repository สำหรับ SQL Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# 3. อัปเดตและติดตั้ง SQL Driver (msodbcsql18)
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

WORKDIR /app

# 4. ติดตั้ง Python Packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. ก๊อปปี้โค้ดทั้งหมด
COPY . .

# 6. สั่งรันแอป (เช็คว่าไฟล์ชื่อ main.py หรือ app.py ถ้าชื่อ app.py ให้แก้บรรทัดล่างเป็น app:app)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]