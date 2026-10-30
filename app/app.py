import os, time
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, redirect, url_for, render_template_string, flash

VERSION = os.getenv("APP_VERSION", "v1").lower()
FEATURES = {"v1": "add", "v2": "update", "v3": "view"}
if VERSION not in FEATURES:
    raise RuntimeError("APP_VERSION must be v1, v2, or v3")
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "local-demo-secret-change-me")

def db():
    return psycopg2.connect(host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"), dbname=os.getenv("DB_NAME", "medicalstore"),
        user=os.getenv("DB_USER", "medicaluser"), password=os.getenv("DB_PASSWORD", "medicalpass"),
        connect_timeout=5)

def initialize_database():
    for attempt in range(30):
        try:
            with db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""CREATE TABLE IF NOT EXISTS medicines (
                        id SERIAL PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL,
                        quantity INTEGER NOT NULL CHECK(quantity >= 0),
                        price NUMERIC(10,2) NOT NULL CHECK(price >= 0),
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
            return
        except psycopg2.OperationalError:
            if attempt == 29: raise
            time.sleep(2)

PAGE = """
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Medical Store {{ version }}</title><style>
body{font:16px Arial;background:#f1f5f9;color:#1e293b;margin:0}header{background:#14532d;color:white;padding:22px 8%}
main{max-width:800px;margin:32px auto;background:white;padding:28px;border-radius:12px;box-shadow:0 3px 16px #0001}
label{display:block;font-weight:bold;margin:14px 0 6px}input{box-sizing:border-box;width:100%;padding:11px;border:1px solid #cbd5e1;border-radius:6px}
button{margin-top:18px;padding:11px 18px;background:#15803d;color:white;border:0;border-radius:6px}
.notice{padding:12px;background:#dcfce7;margin:12px 0;border-radius:6px}.error{background:#fee2e2}
table{width:100%;border-collapse:collapse;margin-top:20px}td,th{text-align:left;padding:12px;border-bottom:1px solid #e2e8f0}
small{color:#64748b}</style></head><body><header><h1>Medical Store Management</h1>
Student ID: 24MIS0126 · {{ version|upper }}</header><main><h2>{{ heading }}</h2><p>{{ description }}</p>
{% with messages=get_flashed_messages(with_categories=true) %}{% for category,message in messages %}
<div class="notice {{ 'error' if category=='error' else '' }}">{{ message }}</div>{% endfor %}{% endwith %}
{% if version=='v1' %}<form method="post" action="/add">
<label>Medicine name</label><input name="name" required maxlength="100" placeholder="Paracetamol">
<label>Quantity</label><input name="quantity" type="number" min="0" required>
<label>Unit price</label><input name="price" type="number" min="0" step="0.01" required>
<button>Add medicine</button></form>
{% elif version=='v2' %}<form method="post" action="/update">
<label>Medicine name</label><input name="name" required maxlength="100">
<label>New quantity</label><input name="quantity" type="number" min="0" required>
<button>Update quantity</button></form>
{% else %}<table><tr><th>Medicine</th><th>Quantity</th><th>Unit price</th></tr>
{% for m in medicines %}<tr><td>{{m.name}}</td><td>{{m.quantity}}</td><td>{{"%.2f"|format(m.price)}}</td></tr>
{% else %}<tr><td colspan="3">No medicines in inventory yet. Add stock through V1.</td></tr>{% endfor %}</table>{% endif %}
<p><small>Shared PostgreSQL inventory · Application {{version|upper}}</small></p></main></body></html>
"""

@app.get("/")
def index():
    headings = {"v1": ("Add Medicine", "Enter medicine details and opening stock."),
                "v2": ("Update Medicine", "Change the quantity of an existing medicine."),
                "v3": ("View Inventory", "Current stock shared by all application versions.")}
    medicines = []
    if VERSION == "v3":
        with db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT name,quantity,price FROM medicines ORDER BY name")
                medicines = cur.fetchall()
    heading, description = headings[VERSION]
    return render_template_string(PAGE, version=VERSION, heading=heading,
                                  description=description, medicines=medicines)

@app.post("/add")
def add():
    if VERSION != "v1": return "Not found", 404
    name = request.form.get("name", "").strip()
    try:
        qty, price = int(request.form["quantity"]), float(request.form["price"])
        if not name or qty < 0 or price < 0: raise ValueError()
        with db() as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO medicines(name,quantity,price) VALUES(%s,%s,%s)
                ON CONFLICT(name) DO UPDATE SET quantity=medicines.quantity+EXCLUDED.quantity,
                price=EXCLUDED.price,updated_at=CURRENT_TIMESTAMP""", (name,qty,price))
        flash(f"{name} stock saved.")
    except (ValueError, KeyError, TypeError):
        flash("Enter a valid name, non-negative quantity and price.", "error")
    return redirect(url_for("index"))

@app.post("/update")
def update():
    if VERSION != "v2": return "Not found", 404
    name = request.form.get("name", "").strip()
    try:
        qty = int(request.form["quantity"])
        if not name or qty < 0: raise ValueError()
        with db() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE medicines SET quantity=%s,updated_at=CURRENT_TIMESTAMP WHERE LOWER(name)=LOWER(%s)",(qty,name))
                changed = cur.rowcount
        flash(f"{name} quantity updated to {qty}." if changed else f"{name} not found. Add it through V1 first.",
              "success" if changed else "error")
    except (ValueError, KeyError, TypeError):
        flash("Enter a valid medicine name and non-negative quantity.", "error")
    return redirect(url_for("index"))

@app.get("/health")
def health():
    return {"status":"ok","version":VERSION}, 200

if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000)
