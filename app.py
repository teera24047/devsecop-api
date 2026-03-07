from fastapi import FastAPI
import os

app = FastAPI()

# จำลองการดึงค่าจาก Environment Variable (ซึ่งสำคัญมากในเรื่อง Security)
ENV_NAME = os.getenv("ENVIRONMENT", "Local")

@app.get("/")
def read_root():
    return {
        "message": "Hello DevSecOps!",
        "environment": ENV_NAME,
        "status": "Healthy"
    }

@app.get("/health")
def health_check():
    # ไว้ให้ Kubernetes คอยเช็คว่าระบบเรายังรอดอยู่ไหม (Liveness Probe)
    return {"status": "ok"}