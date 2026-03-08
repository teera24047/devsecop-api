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

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 2. Data Models ---
class Product(BaseModel):
    name: str
    price: float

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: str
    phone: str

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
            #product-section, #register-section { display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <div id="login-section">
                <h2 class="text-center mb-4">🔒 เข้าสู่ระบบ</h2>
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <input type="text" id="l_username" class="form-control mb-2" placeholder="ชื่อผู้ใช้ (Username)">
                        <input type="password" id="l_password" class="form-control mb-3" placeholder="รหัสผ่าน (Password)">
                        <button onclick="login()" class="btn btn-primary w-100 mb-2">เข้าสู่ระบบ</button>
                        <button onclick="toggleView('register')" class="btn btn-outline-secondary w-100">ยังไม่มีบัญชี? สมัครสมาชิกที่นี่</button>
                        <div id="login-message" class="text-center mt-3 text-danger"></div>
                    </div>
                </div>
            </div>

            <div id="register-section">
                <h2 class="text-center mb-4">📝 สมัครสมาชิกใหม่</h2>
                <div class="row justify-content-center">
                    <div class="col-md-8">
                        <div class="row mb-2">
                            <div class="col"><input type="text" id="r_fname" class="form-control" placeholder="ชื่อจริง"></div>
                            <div class="col"><input type="text" id="r_lname" class="form-control" placeholder="นามสกุล"></div>
                        </div>
                        <input type="email" id="r_email" class="form-control mb-2" placeholder="อีเมล (Email)">
                        <input type="text" id="r_phone" class="form-control mb-3" placeholder="เบอร์โทรศัพท์">
                        <hr>
                        <input type="text" id="r_username" class="form-control mb-2" placeholder="ตั้งชื่อผู้ใช้ (Username)">
                        <input type="password" id="r_password" class="form-control mb-3" placeholder="ตั้งรหัสผ่าน (Password)">
                        
                        <button onclick="register()" class="btn btn-success w-100 mb-2">ยืนยันการสมัครสมาชิก</button>
                        <button onclick="toggleView('login')" class="btn btn-outline-secondary w-100">กลับไปหน้าเข้าสู่ระบบ</button>
                        <div id="register-message" class="text-center mt-3 text-danger"></div>
                    </div>
                </div>
            </div>

            <div id="product-section">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2>📦 ระบบจัดการสินค้า</h2>
                    <button onclick="logout()" class="btn btn-danger btn-sm">ออกจากระบบ</button>
                </div>
                <div class="row g-3 mb-4">
                    <div class="col-md-6"><input type="text" id="p_name" class="form-control" placeholder="ชื่อสินค้า"></div>
                    <div class="col-md-4"><input type="number" id="p_price" class="form-control" placeholder="ราคา"></div>
                    <div class="col-md-2"><button onclick="saveProduct()" class="btn btn-success w-100">บันทึก</button></div>
                </div>
                <table class="table table-hover">
                    <thead class="table-dark"><tr><th>สินค้า</th><th>ราคา (บาท)</th></tr></thead>
                    <tbody id="product-table"></tbody>
                </table>
            </div>
        </div>

        <script>
            // สลับหน้าจอ
            function toggleView(view) {
                document.getElementById('login-section').style.display = view === 'login' ? 'block' : 'none';
                document.getElementById('register-section').style.display = view === 'register' ? 'block' : 'none';
                document.getElementById('product-section').style.display = view === 'product' ? 'block' : 'none';
                document.getElementById('login-message').innerText = '';
                document.getElementById('register-message').innerText = '';
            }

            // ระบบ Auth
            async function register() {
                const data = {
                    first_name: document.getElementById('r_fname').value,
                    last_name: document.getElementById('r_lname').value,
                    email: document.getElementById('r_email').value,
                    phone: document.getElementById('r_phone').value,
                    username: document.getElementById('r_username').value,
                    password: document.getElementById('r_password').value
                };

                if(!data.username || !data.password || !data.first_name) {
                    return document.getElementById('register-message').innerText = "กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน";
                }

                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                if(res.ok) {
                    alert("สมัครสมาชิกสำเร็จ! กรุณาล็อกอิน");
                    toggleView('login');
                } else {
                    document.getElementById('register-message').innerText = "ชื่อผู้ใช้นี้มีคนใช้แล้ว หรือข้อมูลไม่ถูกต้อง";
                }
            }

            async function login() {
                const u = document.getElementById('l_username').value;
                const p = document.getElementById('l_password').value;
                if(!u || !p) return;

                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username: u, password: p})
                });

                if(res.ok) {
                    toggleView('product');
                    fetchProducts();
                } else {
                    document.getElementById('login-message').innerText = "ชื่อผู้ใช้ หรือ รหัสผ่านไม่ถูกต้อง!";
                }
            }

            function logout() {
                document.getElementById('l_username').value = '';
                document.getElementById('l_password').value = '';
                toggleView('login');
            }

            // ระบบสินค้า
            async function fetchProducts() {
                const response = await fetch('/api/products');
                const products = await response.json();
                const tableBody = document.getElementById('product-table');
                tableBody.innerHTML = products.map(p => `<tr><td>${p.name}</td><td>${p.price.toLocaleString()}</td></tr>`).join('');
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
def register(user: UserRegister):
    conn = None
    try:
        hashed_pwd = pwd_context.hash(user.password)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Users (username, password_hash, first_name, last_name, email, phone) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user.username, hashed_pwd, user.first_name, user.last_name, user.email, user.phone))
        conn.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Registration failed. Username might exist.")
    finally:
        if conn: conn.close()

@app.post("/api/login")
def login(user: UserLogin):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM Users WHERE username = ?", (user.username,))
        row = cursor.fetchone()
        
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