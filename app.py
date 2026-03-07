from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # เพิ่มส่วนนี้
from pydantic import BaseModel
from typing import List

app = FastAPI()

# ปลดล็อกให้หน้าเว็บดึงข้อมูลได้ (Security Best Practice)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Product(BaseModel):
    id: int
    name: str
    price: float
    image_url: str

db_products = [
    {"id": 1, "name": "Cyber Armor Jacket", "price": 2500, "image_url": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=500"},
    {"id": 2, "name": "DevSecOps Helmet", "price": 1200, "image_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=500"},
    {"id": 3, "name": "Security Key V2", "price": 800, "image_url": "https://images.unsplash.com/photo-1633265486064-086b219458ec?w=500"}
]

@app.get("/api/products", response_model=List[Product])
def get_products():
    return db_products