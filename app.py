from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sqlite3

app = FastAPI()

# ---------------------------------------------------------
# ส่วนที่ 1: สร้าง Database และข้อมูลจำลองโดยอัตโนมัติ
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect('secure_shop.db')
    c = conn.cursor()
    # สร้างตารางสินค้า
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, image TEXT)')
    c.execute('DELETE FROM products') # ล้างข้อมูลเก่าทุกครั้งที่เริ่มระบบใหม่
    
    # ข้อมูลสินค้าสไตล์ DevSecOps
    products = [
        (1, "DevSecOps Shield v2", 1500, "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=500"),
        (2, "Cyber Armor Jacket", 3200, "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=500"),
        (3, "Hardware Security Key", 850, "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=500")
    ]
    c.executemany('INSERT INTO products VALUES (?,?,?,?)', products)
    conn.commit()
    conn.close()

init_db() # สั่งทำงานตอนเปิดแอป

# ---------------------------------------------------------
# ส่วนที่ 2: เส้นทางสำหรับส่งหน้าเว็บ (Frontend)
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def read_root():
    # เมื่อมีคนเข้าเว็บหน้าแรก ให้โหลดไฟล์ index.html ไปแสดง
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# ---------------------------------------------------------
# ส่วนที่ 3: เส้นทางสำหรับดึงข้อมูลสินค้า (API)
# ---------------------------------------------------------
@app.get("/api/products")
def get_products():
    conn = sqlite3.connect('secure_shop.db')
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    rows = c.fetchall()
    conn.close()
    
    # แปลงข้อมูลจาก Database เป็น JSON
    return [{"id": r[0], "name": r[1], "price": r[2], "image": r[3]} for r in rows]

if __name__ == "__main__":
    import uvicorn
    # บังคับรันที่ Port 80 ชัวร์ๆ แก้ปัญหา 502
    uvicorn.run(app, host="0.0.0.0", port=80)