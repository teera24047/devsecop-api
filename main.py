from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pyodbc
import os

app = FastAPI()

# --- 1. การตั้งค่าการเชื่อมต่อฐานข้อมูล (Global Variable) ---
# ย้ายออกมาไว้ข้างนอกเพื่อให้ทุกฟังก์ชันเรียกใช้ได้ และแก้ปัญหา 'conn_str' is not defined
conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:teera-sql-server.database.windows.net,1433;" 
    "Database=inventory;" # อัปเดตตามที่คุณบอนยืนยัน
    "Uid=teeraadmin;" 
    "Pwd=Teera!@#24047;" # รหัสผ่านของคุณบอน
    "Encrypt=yes;"
    "TrustServerCertificate=yes;" # เปลี่ยนเป็น yes เพื่อให้รันบน Container ได้ราบรื่น
    "Connection Timeout=30;"
)

# ฟังก์ชันกลางสำหรับเชื่อมต่อ DB
def get_db_connection():
    return pyodbc.connect(conn_str)

# --- 2. Data Model ---
class Product(BaseModel):
    name: str
    price: float

# --- 3. หน้าเว็บ Frontend (HTML/JS) ---
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>Azure SQL Product Store</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f4f7f6; padding-top: 50px; }
            .container { max-width: 800px; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
            .btn-save { background-color: #28a745; color: white; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2 class="text-center mb-4">📦 ระบบจัดการสินค้า (Azure SQL)</h2>
            <div class="row g-3 mb-4">
                <div class="col-md-6">
                    <input type="text" id="p_name" class="form-control" placeholder="ชื่อสินค้า">
                </div>
                <div class="col-md-4">
                    <input type="number" id="p_price" class="form-control" placeholder="ราคา">
                </div>
                <div class="col-md-2">
                    <button onclick="saveProduct()" class="btn btn-save w-100">บันทึก</button>
                </div>
            </div>
            <hr>
            <table class="table table-hover">
                <thead class="table-dark">
                    <tr><th>สินค้า</th><th>ราคา (บาท)</th></tr>
                </thead>
                <tbody id="product-table"></tbody>
            </table>
        </div>
        <script>
            async function fetchProducts() {
                try {
                    const response = await fetch('/api/products');
                    const products = await response.json();
                    const tableBody = document.getElementById('product-table');
                    if (products.error) {
                        console.error(products.error);
                        return;
                    }
                    tableBody.innerHTML = products.map(p => `
                        <tr><td>${p.name}</td><td>${p.price.toLocaleString()}</td></tr>
                    `).join('');
                } catch (err) { console.error("Fetch error:", err); }
            }

            async function saveProduct() {
                const name = document.getElementById('p_name').value;
                const price = document.getElementById('p_price').value;
                if(!name || !price) return alert('กรุณากรอกข้อมูลให้ครบ');

                await fetch('/api/products', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name: name, price: parseFloat(price) })
                });

                document.getElementById('p_name').value = '';
                document.getElementById('p_price').value = '';
                fetchProducts();
            }
            fetchProducts();
        </script>
    </body>
    </html>
    """

# --- 4. API Endpoints (Backend) ---

@app.get("/api/products")
def list_products():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # ดึงข้อมูลจากตาราง Products
        cursor.execute("SELECT name, price FROM Products")
        rows = cursor.fetchall()
        products = [{"name": row[0], "price": float(row[1])} for row in rows]
        return products
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

@app.post("/api/products")
def create_product(product: Product):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # บันทึกข้อมูล (ตรวจสอบชื่อตาราง Products ใน DB ของคุณบอนด้วยนะครับ)
        cursor.execute("INSERT INTO Products (name, price) VALUES (?, ?)", (product.name, product.price))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        print(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            conn.close()