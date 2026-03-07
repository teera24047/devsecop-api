import sqlite3
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

app = FastAPI()

# ---------------------------------------------------------
# 1. ระบบฐานข้อมูล SQL (สร้างและล้างข้อมูลอัตโนมัติ)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("devsecops.db")
    cursor = conn.cursor()
    # สร้างตาราง SQL
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            image_url TEXT NOT NULL
        )
    """)
    # ล้างข้อมูลเก่าและใส่ข้อมูลใหม่ทุกครั้งที่แอปเริ่มทำงาน
    cursor.execute("DELETE FROM products")
    sample_data = [
        (1, "Cyber Armor Jacket", 2500.0, "https://images.unsplash.com/photo-1551434678-e076c223a692?w=500"),
        (2, "DevSecOps Helmet", 1200.0, "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=500"),
        (3, "Security Key V2", 800.0, "https://images.unsplash.com/photo-1633265486064-086b219458ec?w=500")
    ]
    cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", sample_data)
    conn.commit()
    conn.close()

init_db()

class Product(BaseModel):
    id: int
    name: str
    price: float
    image_url: str

# ---------------------------------------------------------
# 2. เส้นทางสำหรับหน้าเว็บ (Frontend)
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>System Error: index.html not found!</h1>"

# ---------------------------------------------------------
# 3. เส้นทางสำหรับ API (Backend)
# ---------------------------------------------------------
@app.get("/api/products", response_model=List[Product])
def get_products():
    conn = sqlite3.connect("devsecops.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, image_url FROM products")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "price": r[2], "image_url": r[3]} for r in rows]

if __name__ == "__main__":
    import uvicorn
    # บังคับรัน Port 80 เพื่อให้ตรงกับ Ingress 100%
    uvicorn.run(app, host="0.0.0.0", port=80)