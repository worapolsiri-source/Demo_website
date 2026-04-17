from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db():
    conn = sqlite3.connect("foodshop.db")
    conn.row_factory = sqlite3.Row
    return conn

# ฟังก์ชันสร้าง 5 ตาราง (Categories, Units, Staffs, Foods, Orders)
def init_db():
    conn = get_db()
    # 1. หมวดหมู่
    conn.execute("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    # 2. หน่วยนับ
    conn.execute("CREATE TABLE IF NOT EXISTS units (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    # 3. พนักงาน
    conn.execute("CREATE TABLE IF NOT EXISTS staffs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT)")
    # 4. อาหาร (เชื่อม FK ไป Categories และ Units)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS foods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        image TEXT,
        stock INTEGER DEFAULT 0,
        category_id INTEGER,
        unit_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories (id),
        FOREIGN KEY (unit_id) REFERENCES units (id)
    )
    """)
    # 5. ประวัติการสั่งซื้อ
    conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        food_id INTEGER,
        amount INTEGER,
        FOREIGN KEY (food_id) REFERENCES foods (id)
    )
    """)
    
    # เพิ่มข้อมูลเริ่มต้น
    conn.execute("INSERT OR IGNORE INTO categories (name) VALUES ('อาหารหลัก'), ('ของหวาน'), ('เครื่องดื่ม')")
    conn.execute("INSERT OR IGNORE INTO units (name) VALUES ('จาน'), ('ชิ้น'), ('แก้ว')")
    conn.execute("INSERT OR IGNORE INTO staffs (name, role) VALUES ('สมชาย', 'เชฟ')")
    
    conn.commit()
    conn.close()

# เรียกใช้งานฟังก์ชันสร้างตาราง
init_db()

# --- ROUTES ---

@app.route("/")
def foodmenu():
    conn = get_db()
    query = """
        SELECT foods.*, categories.name as cat_name, units.name as unit_name 
        FROM foods 
        LEFT JOIN categories ON foods.category_id = categories.id
        LEFT JOIN units ON foods.unit_id = units.id
    """
    foods = conn.execute(query).fetchall()
    conn.close()
    return render_template("foodmenu.html", foods=foods)

@app.route("/append", methods=["GET", "POST"])
def append():
    conn = get_db()
    if request.method == "POST":
        conn.execute("INSERT INTO foods (name, price, stock, image, category_id, unit_id) VALUES (?, ?, ?, ?, ?, ?)",
                     (request.form["name"], request.form["price"], request.form["stock"], 
                      request.form["image"], request.form["category_id"], request.form["unit_id"]))
        conn.commit()
        conn.close()
        return redirect(url_for('foodmenu'))
    
    cats = conn.execute("SELECT * FROM categories").fetchall()
    units = conn.execute("SELECT * FROM units").fetchall()
    conn.close()
    return render_template("append.html", categories=cats, units=units)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    if request.method == "POST":
        conn.execute("UPDATE foods SET name=?, price=?, stock=?, image=?, category_id=?, unit_id=? WHERE id=?",
                     (request.form["name"], request.form["price"], request.form["stock"], 
                      request.form["image"], request.form["category_id"], request.form["unit_id"], id))
        conn.commit()
        conn.close()
        return redirect(url_for('foodmenu'))
    
    food = conn.execute("SELECT * FROM foods WHERE id=?", (id,)).fetchone()
    cats = conn.execute("SELECT * FROM categories").fetchall()
    units = conn.execute("SELECT * FROM units").fetchall()
    conn.close()
    return render_template("edit.html", food=food, categories=cats, units=units)

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM foods WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('foodmenu'))

if __name__ == "__main__":
    app.run(debug=True)