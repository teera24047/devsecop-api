from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pyodbc
import os

app = FastAPI()

# --- 1. การเชื่อมต่อฐานข้อมูล Azure SQL ---
def get_db_connection():
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        # 1. Server ต้องตรงกับที่เห็นใน Azure (teera-sql-server)
        "Server=tcp:teera-sql-server.database.windows.net,1433;" 
        # 2. Database Name (ต้องระบุชื่อ DB ที่คุณสร้างไว้ เช่น my-db)
        "Database=teera-db;" 
        # 3. Username (ตัดคำว่า your- ออก)
        "Uid=teeraadmin;" 
        # 4. Password (ตัดคำว่า your- ออก)
        "Pwd=Teera!@#24047;" 
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

# --- 2. Data Model (โครงสร้างข้อมูลสินค้า) ---
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
                <tbody id="product-table">
                    </tbody>
            </table>
        </div>

        <script>
            // ดึงข้อมูลสินค้ามาแสดง
            async function fetchProducts() {
                const response = await fetch('/api/products');
                const products = await response.json();
                const tableBody = document.getElementById('product-table');
                tableBody.innerHTML = products.map(p => `
                    <tr><td>${p.name}</td><td>${p.price.toLocaleString()}</td></tr>
                `).join('');
            }

            // บันทึกข้อมูลสินค้าใหม่
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
                fetchProducts(); // โหลดข้อมูลใหม่
            }

            fetchProducts(); // รันตอนเปิดหน้าเว็บ
        </script>
    </body>
    </html>
    """

# --- 4. API Endpoints (Backend) ---

@app.get("/api/products")
# ตัวอย่างการแก้ในฟังก์ชัน list_products หรือ add_product
def list_products():
    conn = None # กำหนดค่าเริ่มต้นไว้ก่อน
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        # ... รัน SQL ...
    except Exception as e:
        print(f"Error connecting to DB: {e}") # ดู Error จริงได้จาก kubectl logs
        return {"error": str(e)}
    finally:
        if conn: # เช็คก่อนว่ามี conn จริงไหมค่อยสั่งปิด
            conn.close()

@app.post("/api/products")
def create_product(product: Product):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Products (name, price) VALUES (?, ?)", (product.name, product.price))
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()