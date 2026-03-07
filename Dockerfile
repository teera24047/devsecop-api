FROM python:3.9-slim

WORKDIR /app

# ติดตั้ง FastAPI และ Uvicorn
RUN pip install fastapi uvicorn

# ก๊อปปี้ไฟล์ทั้งหมดเข้า Container
COPY . .

# สั่งรัน API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]