import os
import pyodbc
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

app = FastAPI()

# ข้อมูลการเชื่อมต่อที่ดึงมาจากที่คุณสร้าง
server = 'teera-sql-server.database.windows.net'
database = 'inventory'
username = 'teeraadmin'
password = 'Teera!@#24047' # nosec B105
driver= '{ODBC Driver 17 for SQL Server}'

conn_str = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'

def get_db_conn():
    # เพิ่ม timeout เพื่อป้องกันการค้างกรณี Network มีปัญหา
    return pyodbc.connect(conn_str, timeout=30)

@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Frontend index.html not found</h1>"

@app.get("/api/products")
def get_products():
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        
        # สร้างตารางและใส่ข้อมูลเริ่มต้น (เฉพาะครั้งแรก)
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Products' AND xtype='U')
            BEGIN
                CREATE TABLE Products (
                    id INT PRIMARY KEY, 
                    name NVARCHAR(100), 
                    price FLOAT, 
                    image_url NVARCHAR(MAX)
                )
                INSERT INTO Products VALUES (1, 'Cyber Armor Jacket', 2500, 'https://images.unsplash.com/photo-1551434678-e076c223a692?w=500')
                INSERT INTO Products VALUES (2, 'DevSecOps Helmet', 1200, 'https://images.unsplash.com/photo-1509062522246-3755977927d7?w=500')
                INSERT INTO Products VALUES (3, 'Security Key V2', 800, 'https://images.unsplash.com/photo-1633265486064-086b219458ec?w=500')
            END
        """)
        conn.commit()

        cursor.execute("SELECT id, name, price, image_url FROM Products")
        rows = cursor.fetchall()
        conn.close()
        
        return [{"id": r[0], "name": r[1], "price": r[2], "image_url": r[3]} for r in rows]
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80) #nosec B104