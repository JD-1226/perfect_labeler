from flask import Flask, render_template, request, redirect, session, send_file
import requests, os, uuid
from reportlab.lib.pagesizes import mm
from reportlab.pdfgen import canvas
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "super-secret-key"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        payload = {
            "email": request.form["email"],
            "password": request.form["password"],
            "data": {
                "tenant_id": request.form["tenant_id"]
            }
        }

        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers={
                "apikey": SUPABASE_KEY,
                "Content-Type": "application/json"
            },
            json=payload
        )

        if r.status_code in (200, 201):
            return redirect("/")
        else:
            # IMPORTANT: show real Supabase error
            return f"Signup failed: {r.text}", 400

    return render_template("register.html")


# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        r = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": SUPABASE_KEY},
            json={
                "email": request.form["email"],
                "password": request.form["password"]
            }
        )

        if r.status_code == 200:
            data = r.json()
            session["access_token"] = data["access_token"]
            session["tenant_id"] = data["user"]["user_metadata"]["tenant_id"]
            return redirect("/dashboard")

        return "Login failed"

    return render_template("login.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "access_token" not in session:
        return redirect("/")
    return render_template("dashboard.html")


# ---------- SAVE DESIGN ----------
@app.route("/save_design", methods=["POST"])
def save_design():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {session['access_token']}",
        "Content-Type": "application/json"
    }

    payload = {
        "id": str(uuid.uuid4()),
        "tenant_id": session["tenant_id"],
        "name": "Label Design",
        "width": 400,
        "height": 200
    }

    requests.post(
        f"{SUPABASE_URL}/rest/v1/receipt_designs",
        headers=headers,
        json=payload
    )

    return "Saved"


# ---------- PRINT PDF ----------
@app.route("/print")
def print_label():
    file_path = "label.pdf"
    c = canvas.Canvas(file_path, pagesize=(400, 200))
    c.drawString(20, 150, "Sample Label Text")
    c.save()
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host= 'localhost', port= '5000', debug=True)
