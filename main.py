from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pyodbc
from passlib.context import CryptContext

app = FastAPI()

# --- 1. การตั้งค่า ---
conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:teera-sql-server.database.windows.net,1433;"
    "Database=inventory;" 
    "Uid=teeraadmin;"
    "Pwd=Teera!@#24047;" # รหัสผ่านของคุณบอน
    "Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
)

def get_db_connection():
    return pyodbc.connect(conn_str)

# ตัวเข้ารหัสผ่าน (Security 🛡️)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 2. Data Models ---
class Product(BaseModel):
    name: str
    price: float

class User(BaseModel):
    username: str
    password: str

# --- 3. หน้าเว็บ Frontend (HTML/JS) ---
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>ระบบจัดการสินค้า (Secure)</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f4f7f6; padding-top: 50px; }
            .container { max-width: 800px; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
            #product-section { display: none; } /* ซ่อนหน้าสินค้าไว้ก่อน */
        </style>
    </head>
    <body>
        <div class="container">
            <div id="auth-section">
                <h2 class="text-center mb-4">🔒 เข้าสู่ระบบ / สมัครสมาชิก</h2>
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <input type="text" id="username" class="form-control mb-2" placeholder="ชื่อผู้ใช้ (Username)">
                        <input type="password" id="password" class="form-control mb-3" placeholder="รหัสผ่าน (Password)">
                        <div class="d-flex justify-content-between">
                            <button onclick="login()" class="btn btn-primary w-100 me-2">เข้าสู่ระบบ</button>
                            <button onclick="register()" class="btn btn-outline-secondary w-100">สมัครสมาชิก</button>
                        </div>
                        <div id="auth-message" class="text-center mt-3 text-danger"></div>
                    </div>
                </div>
            </div>

            <div id="product-section">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>📦 ระบบจัดการสินค้า</h2>
                    <button onclick="logout()" class="btn btn-danger btn-sm">ออกจากระบบ</button>
                </div>
                <div class="row g-3 mb-4">
                    <div class="col-md-6">
                        <input type="text" id="p_name" class="form-control" placeholder="ชื่อสินค้า">
                    </div>
                    <div class="col-md-4">
                        <input type="number" id="p_price" class="form-control" placeholder="ราคา">
                    </div>
                    <div class="col-md-2">
                        <button onclick="saveProduct()" class="btn btn-success w-100">บันทึก</button>
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
        </div>

        <script>
            // --- ระบบ Auth ---
            async function register() {
                const u = document.getElementById('username').value;
                const p = document.getElementById('password').value;
                if(!u || !p) return alert("กรอกข้อมูลให้ครบครับ");

                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username: u, password: p})
                });
                
                if(res.ok) {
                    alert("สมัครสมาชิกสำเร็จ! ล็อกอินได้เลยครับ");
                } else {
                    document.getElementById('auth-message').innerText = "ชื่อผู้ใช้นี้มีคนใช้แล้ว หรือเกิดข้อผิดพลาด";
                }
            }

            async function login() {
                const u = document.getElementById('username').value;
                const p = document.getElementById('password').value;
                if(!u || !p) return;

                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username: u, password: p})
                });

                if(res.ok) {
                    // ล็อกอินผ่าน -> ซ่อนหน้า Auth, โชว์หน้า Product
                    document.getElementById('auth-section').style.display = 'none';
                    document.getElementById('product-section').style.display = 'block';
                    fetchProducts(); // โหลดข้อมูลสินค้า
                } else {
                    document.getElementById('auth-message').innerText = "ชื่อผู้ใช้ หรือ รหัสผ่านไม่ถูกต้อง!";
                }
            }

            function logout() {
                document.getElementById('username').value = '';
                document.getElementById('password').value = '';
                document.getElementById('auth-section').style.display = 'block';
                document.getElementById('product-section').style.display = 'none';
            }

            // --- ระบบสินค้า ---
            async function fetchProducts() {
                const response = await fetch('/api/products');
                const products = await response.json();
                const tableBody = document.getElementById('product-table');
                tableBody.innerHTML = products.map(p => `
                    <tr><td>${p.name}</td><td>${p.price.toLocaleString()}</td></tr>
                `).join('');
            }

            async function saveProduct() {
                const name = document.getElementById('p_name').value;
                const price = document.getElementById('p_price').value;
                if(!name || !price) return;

                await fetch('/api/products', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name: name, price: parseFloat(price) })
                });

                document.getElementById('p_name').value = '';
                document.getElementById('p_price').value = '';
                fetchProducts();
            }
        </script>
    </body>
    </html>
    """

# --- 4. API Endpoints ---

@app.post("/api/register")
def register(user: User):
    conn = None
    try:
        # เข้ารหัสผ่านก่อนลง Database
        hashed_pwd = pwd_context.hash(user.password)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (username, password_hash) VALUES (?, ?)", (user.username, hashed_pwd))
        conn.commit()
        return {"message": "User created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Username already exists or DB Error")
    finally:
        if conn: conn.close()

@app.post("/api/login")
def login(user: User):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM Users WHERE username = ?", (user.username,))
        row = cursor.fetchone()
        
        # ถอดรหัสมาเทียบกัน
        if row and pwd_context.verify(user.password, row[0]):
            return {"message": "Login successful"}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    finally:
        if conn: conn.close()

@app.get("/api/products")
def list_products():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, price FROM Products")
        rows = cursor.fetchall()
        return [{"name": row[0], "price": float(row[1])} for row in rows]
    finally:
        if conn: conn.close()

@app.post("/api/products")
def create_product(product: Product):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Products (name, price) VALUES (?, ?)", (product.name, product.price))
        conn.commit()
        return {"status": "success"}
    finally:
        if conn: conn.close()