from pathlib import Path
import textwrap, os, json, zipfile

root = Path("/mnt/data/transport24")
if root.exists():
    import shutil
    shutil.rmtree(root)

files = {}

files["docker-compose.yml"] = r'''
services:
  db:
    image: postgres:17-alpine
    container_name: transport24-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: transport24
      POSTGRES_USER: transport24
      POSTGRES_PASSWORD: transport24_dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U transport24 -d transport24"]
      interval: 5s
      timeout: 5s
      retries: 10

  backend:
    build: ./backend
    container_name: transport24-api
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://transport24:transport24_dev_password@db:5432/transport24
      JWT_SECRET: change-this-secret-before-production
      ACCESS_TOKEN_EXPIRE_MINUTES: 480
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
'''

files["backend/Dockerfile"] = r'''
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

files["backend/requirements.txt"] = r'''
fastapi==0.117.1
uvicorn[standard]==0.36.0
psycopg2-binary==2.9.10
PyJWT==2.10.1
pwdlib[argon2]==0.2.1
python-multipart==0.0.20
'''

files["database/schema.sql"] = r'''
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'employee'
        CHECK (role IN ('admin', 'employee')),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(30),
    email VARCHAR(120),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    service_type VARCHAR(20) NOT NULL
        CHECK (service_type IN ('people', 'objects')),
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    service_date DATE NOT NULL,
    service_time TIME NOT NULL,
    price NUMERIC(12,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'scheduled', 'completed', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS people_services (
    service_id INTEGER PRIMARY KEY REFERENCES services(id) ON DELETE CASCADE,
    passengers INTEGER NOT NULL CHECK (passengers > 0)
);

CREATE TABLE IF NOT EXISTS object_services (
    service_id INTEGER PRIMARY KEY REFERENCES services(id) ON DELETE CASCADE,
    object_description TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0)
);

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    service_id INTEGER UNIQUE NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    payment_method VARCHAR(20) NOT NULL DEFAULT 'cash'
        CHECK (payment_method IN ('cash', 'other')),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (payment_status IN ('pending', 'paid')),
    paid_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_services_date ON services(service_date);
CREATE INDEX IF NOT EXISTS idx_services_customer ON services(customer_id);
CREATE INDEX IF NOT EXISTS idx_services_employee ON services(employee_id);

-- The 8 initial employee accounts are created by backend/startup code.
-- Passwords are hashed with Argon2 and are never stored in plaintext.
'''

files["backend/main.py"] = r'''
import os
import time
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

import jwt
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from pwdlib import PasswordHash

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://transport24:transport24_dev_password@localhost:5432/transport24",
)
JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-secret")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

app = FastAPI(
    title="Transport24 API",
    version="1.0.0",
    description="Simple 24/7 people and object transportation management system.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


INITIAL_EMPLOYEES = [
    ("employee01", "Employee 01", "employee", "Transport24-01!"),
    ("employee02", "Employee 02", "employee", "Transport24-02!"),
    ("employee03", "Employee 03", "employee", "Transport24-03!"),
    ("employee04", "Employee 04", "employee", "Transport24-04!"),
    ("employee05", "Employee 05", "employee", "Transport24-05!"),
    ("employee06", "Employee 06", "employee", "Transport24-06!"),
    ("employee07", "Employee 07", "employee", "Transport24-07!"),
    ("employee08", "Employee 08", "admin", "Transport24-08!"),
]


def db():
    for _ in range(20):
        try:
            return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        except psycopg2.OperationalError:
            time.sleep(1)
    raise RuntimeError("Database is unavailable")


def init_employees():
    conn = db()
    try:
        with conn.cursor() as cur:
            for username, full_name, role, password in INITIAL_EMPLOYEES:
                cur.execute(
                    """
                    INSERT INTO employees
                        (username, password_hash, full_name, role)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (username) DO NOTHING
                    """,
                    (username, password_hash.hash(password), full_name, role),
                )
        conn.commit()
    finally:
        conn.close()


@app.on_event("startup")
def startup():
    # schema.sql runs before the API becomes healthy.
    init_employees()


def authenticate(username: str, password: str):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, password_hash, full_name, role, active
                FROM employees
                WHERE username = %s
                """,
                (username,),
            )
            user = cur.fetchone()
    finally:
        conn.close()

    if not user or not user["active"]:
        return None
    if not password_hash.verify(password, user["password_hash"]):
        return None
    return user


def create_token(user):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user["id"]),
        "username": user["username"],
        "role": user["role"],
        "exp": now + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def current_user(token: str = Depends(oauth2_scheme)):
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise credentials_error

    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, full_name, role, active
                FROM employees
                WHERE id = %s
                """,
                (user_id,),
            )
            user = cur.fetchone()
    finally:
        conn.close()

    if not user or not user["active"]:
        raise credentials_error
    return user


class CustomerIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None


class ServiceIn(BaseModel):
    customer_id: int
    service_type: str
    origin: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    service_date: date
    service_time: str
    price: Decimal = Field(default=Decimal("0"), ge=0)
    status: str = "pending"
    notes: Optional[str] = None
    passengers: Optional[int] = Field(default=None, ge=1)
    object_description: Optional[str] = None
    quantity: Optional[int] = Field(default=None, ge=1)


class PaymentIn(BaseModel):
    amount: Decimal = Field(ge=0)
    payment_method: str = "cash"
    payment_status: str = "paid"


@app.get("/api/health")
def health():
    conn = db()
    conn.close()
    return {"status": "ok", "service": "transport24"}


@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
        )

    return {
        "access_token": create_token(user),
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
        },
    }


@app.get("/api/me")
def me(user=Depends(current_user)):
    return user


@app.get("/api/employees")
def employees(user=Depends(current_user)):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, full_name, role, active, created_at
                FROM employees
                ORDER BY id
                """
            )
            return cur.fetchall()
    finally:
        conn.close()


@app.get("/api/customers")
def customers(user=Depends(current_user)):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, full_name, phone, email, notes, created_at
                FROM customers
                ORDER BY full_name
                """
            )
            return cur.fetchall()
    finally:
        conn.close()


@app.post("/api/customers")
def create_customer(data: CustomerIn, user=Depends(current_user)):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO customers (full_name, phone, email, notes)
                VALUES (%s, %s, %s, %s)
                RETURNING id, full_name, phone, email, notes, created_at
                """,
                (data.full_name, data.phone, data.email, data.notes),
            )
            result = cur.fetchone()
        conn.commit()
        return result
    finally:
        conn.close()


@app.get("/api/services")
def services(user=Depends(current_user)):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    s.id,
                    s.service_type,
                    s.origin,
                    s.destination,
                    s.service_date,
                    s.service_time,
                    s.price,
                    s.status,
                    s.notes,
                    c.full_name AS customer_name,
                    e.full_name AS employee_name,
                    ps.passengers,
                    os.object_description,
                    os.quantity,
                    COALESCE(p.payment_status, 'pending') AS payment_status
                FROM services s
                JOIN customers c ON c.id = s.customer_id
                JOIN employees e ON e.id = s.employee_id
                LEFT JOIN people_services ps ON ps.service_id = s.id
                LEFT JOIN object_services os ON os.service_id = s.id
                LEFT JOIN payments p ON p.service_id = s.id
                ORDER BY s.service_date DESC, s.service_time DESC, s.id DESC
                """
            )
            return cur.fetchall()
    finally:
        conn.close()


@app.post("/api/services")
def create_service(data: ServiceIn, user=Depends(current_user)):
    if data.service_type not in {"people", "objects"}:
        raise HTTPException(400, "service_type must be people or objects")

    if data.status not in {"pending", "scheduled", "completed", "cancelled"}:
        raise HTTPException(400, "Invalid service status")

    if data.service_type == "people" and not data.passengers:
        raise HTTPException(400, "Passengers is required for people service")

    if data.service_type == "objects" and not data.object_description:
        raise HTTPException(400, "Object description is required")

    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM customers WHERE id = %s",
                (data.customer_id,),
            )
            if not cur.fetchone():
                raise HTTPException(404, "Customer not found")

            cur.execute(
                """
                INSERT INTO services
                    (customer_id, employee_id, service_type, origin, destination,
                     service_date, service_time, price, status, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
                """,
                (
                    data.customer_id,
                    user["id"],
                    data.service_type,
                    data.origin,
                    data.destination,
                    data.service_date,
                    data.service_time,
                    data.price,
                    data.status,
                    data.notes,
                ),
            )
            service_id = cur.fetchone()["id"]

            if data.service_type == "people":
                cur.execute(
                    """
                    INSERT INTO people_services (service_id, passengers)
                    VALUES (%s, %s)
                    """,
                    (service_id, data.passengers),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO object_services
                        (service_id, object_description, quantity)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        service_id,
                        data.object_description,
                        data.quantity or 1,
                    ),
                )

            cur.execute(
                """
                INSERT INTO payments
                    (service_id, amount, payment_method, payment_status)
                VALUES (%s, %s, 'cash', 'pending')
                """,
                (service_id, data.price),
            )

        conn.commit()
        return {"id": service_id, "message": "Service created"}
    finally:
        conn.close()


@app.post("/api/services/{service_id}/payment")
def update_payment(
    service_id: int,
    data: PaymentIn,
    user=Depends(current_user),
):
    if data.payment_method not in {"cash", "other"}:
        raise HTTPException(400, "Invalid payment method")

    if data.payment_status not in {"pending", "paid"}:
        raise HTTPException(400, "Invalid payment status")

    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE payments
                SET amount = %s,
                    payment_method = %s,
                    payment_status = %s,
                    paid_at = CASE
                        WHEN %s = 'paid' THEN CURRENT_TIMESTAMP
                        ELSE NULL
                    END
                WHERE service_id = %s
                RETURNING id, service_id, amount, payment_method,
                          payment_status, paid_at
                """,
                (
                    data.amount,
                    data.payment_method,
                    data.payment_status,
                    data.payment_status,
                    service_id,
                ),
            )
            result = cur.fetchone()

            if not result:
                raise HTTPException(404, "Service/payment not found")

        conn.commit()
        return result
    finally:
        conn.close()


@app.get("/api/dashboard")
def dashboard(user=Depends(current_user)):
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) FILTER (WHERE service_type = 'people') AS people,
                    COUNT(*) FILTER (WHERE service_type = 'objects') AS objects,
                    COUNT(*) AS total,
                    COALESCE(SUM(price), 0) AS revenue
                FROM services
                WHERE service_date = CURRENT_DATE
                  AND status <> 'cancelled'
                """
            )
            stats = cur.fetchone()

            cur.execute(
                """
                SELECT COUNT(*) AS pending_payments
                FROM payments p
                JOIN services s ON s.id = p.service_id
                WHERE p.payment_status = 'pending'
                  AND s.status <> 'cancelled'
                """
            )
            pending = cur.fetchone()["pending_payments"]

            return {
                "people": stats["people"],
                "objects": stats["objects"],
                "total": stats["total"],
                "revenue": stats["revenue"],
                "pending_payments": pending,
            }
    finally:
        conn.close()
'''

files["frontend/index.html"] = r'''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Transport24</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
<div id="app"></div>
<script src="app.js"></script>
</body>
</html>
'''

files["frontend/style.css"] = r'''
:root {
  --bg: #080a0d;
  --panel: #11151a;
  --panel2: #181d23;
  --line: #2a3139;
  --text: #eef2f6;
  --muted: #9ca7b3;
  --blue: #5d83ff;
  --blue2: #345ee8;
  --danger: #e26d76;
  --ok: #6fcf97;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: "Courier New", Courier, monospace;
}

button, input, select, textarea {
  font: inherit;
}

button {
  cursor: pointer;
}

.hidden { display: none !important; }

.login {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.login-card {
  width: min(420px, 100%);
  background: var(--panel);
  border: 1px solid var(--line);
  padding: 34px;
  box-shadow: 0 20px 60px rgba(0,0,0,.35);
}

.brand {
  letter-spacing: 4px;
  font-size: 28px;
  font-weight: 700;
}

.tagline {
  color: var(--muted);
  margin: 8px 0 28px;
}

label {
  display: block;
  margin: 16px 0 7px;
  color: var(--muted);
  font-size: 13px;
}

input, select, textarea {
  width: 100%;
  background: #0b0e12;
  color: var(--text);
  border: 1px solid var(--line);
  padding: 12px;
  outline: none;
}

input:focus, select:focus, textarea:focus {
  border-color: var(--blue);
}

textarea {
  min-height: 90px;
  resize: vertical;
}

.primary, .secondary {
  border: 1px solid var(--blue);
  padding: 12px 16px;
  color: var(--text);
  background: var(--blue2);
}

.secondary {
  background: var(--panel2);
}

.full { width: 100%; }

.error {
  color: var(--danger);
  min-height: 20px;
  margin: 12px 0;
}

.app-shell {
  min-height: 100vh;
}

.topbar {
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid var(--line);
  background: var(--panel);
}

.topbar .brand { font-size: 19px; }

.userbox {
  display: flex;
  gap: 14px;
  align-items: center;
  color: var(--muted);
}

.layout {
  display: grid;
  grid-template-columns: 210px 1fr;
  min-height: calc(100vh - 68px);
}

.sidebar {
  border-right: 1px solid var(--line);
  background: #0d1014;
  padding: 18px 12px;
}

.nav-btn {
  width: 100%;
  text-align: left;
  border: 0;
  border-left: 2px solid transparent;
  background: transparent;
  color: var(--muted);
  padding: 12px;
  margin-bottom: 4px;
}

.nav-btn:hover, .nav-btn.active {
  color: var(--text);
  border-left-color: var(--blue);
  background: var(--panel2);
}

.content {
  padding: 28px;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

h1, h2, h3 { margin-top: 0; }

.muted { color: var(--muted); }

.cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin: 20px 0 28px;
}

.card {
  background: var(--panel);
  border: 1px solid var(--line);
  padding: 18px;
}

.card .number {
  font-size: 28px;
  margin-top: 8px;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}

.form-card {
  background: var(--panel);
  border: 1px solid var(--line);
  padding: 22px;
  margin-bottom: 24px;
}

.grid2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--line);
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 850px;
}

th, td {
  text-align: left;
  padding: 11px 12px;
  border-bottom: 1px solid var(--line);
}

th {
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
}

.badge {
  display: inline-block;
  border: 1px solid var(--line);
  padding: 4px 7px;
  font-size: 11px;
}

.success { color: var(--ok); }
.warning { color: #e7c66b; }

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .sidebar {
    border-right: 0;
    border-bottom: 1px solid var(--line);
    display: flex;
    overflow-x: auto;
  }
  .nav-btn { width: auto; white-space: nowrap; }
  .cards { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 600px) {
  .content { padding: 16px; }
  .topbar { padding: 0 14px; }
  .userbox span { display: none; }
  .cards, .grid2 { grid-template-columns: 1fr; }
}
'''

files["frontend/app.js"] = r'''
const API = "http://localhost:8000/api";
let token = localStorage.getItem("transport24_token");
let currentUser = null;

const app = document.getElementById("app");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function api(path, options = {}) {
  const headers = {
    ...(options.body instanceof FormData ? {} : {"Content-Type": "application/json"}),
    ...(options.headers || {})
  };

  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(API + path, {...options, headers});

  if (response.status === 401) {
    logout();
    throw new Error("Session expired");
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }

  return data;
}

function renderLogin(message = "") {
  app.innerHTML = `
    <div class="login">
      <form class="login-card" id="loginForm">
        <div class="brand">TRANSPORT24</div>
        <div class="tagline">24 / 7 · PEOPLE & OBJECTS</div>

        <label>Username</label>
        <input id="username" autocomplete="username" required>

        <label>Password</label>
        <input id="password" type="password" autocomplete="current-password" required>

        <div class="error">${escapeHtml(message)}</div>

        <button class="primary full">ENTER SYSTEM</button>
      </form>
    </div>
  `;

  document.getElementById("loginForm").addEventListener("submit", login);
}

async function login(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);

  try {
    const response = await fetch(API + "/login", {
      method: "POST",
      headers: {"Content-Type": "application/x-www-form-urlencoded"},
      body
    });

    const data = await response.json();

    if (!response.ok) {
      renderLogin(data.detail || "Login failed");
      return;
    }

    token = data.access_token;
    localStorage.setItem("transport24_token", token);
    currentUser = data.user;

    renderApp();
  } catch (error) {
    renderLogin("Cannot connect to the API.");
  }
}

function logout() {
  token = null;
  currentUser = null;
  localStorage.removeItem("transport24_token");
  renderLogin();
}

function renderApp() {
  app.innerHTML = `
    <div class="app-shell">
      <header class="topbar">
        <div class="brand">TRANSPORT24</div>
        <div class="userbox">
          <span id="userLabel"></span>
          <button class="secondary" onclick="logout()">LOGOUT</button>
        </div>
      </header>

      <div class="layout">
        <aside class="sidebar">
          <button class="nav-btn active" data-page="dashboard">Dashboard</button>
          <button class="nav-btn" data-page="customers">Customers</button>
          <button class="nav-btn" data-page="people">People service</button>
          <button class="nav-btn" data-page="objects">Object service</button>
          <button class="nav-btn" data-page="records">Records</button>
          <button class="nav-btn" data-page="employees">Employees</button>
        </aside>

        <main class="content" id="content"></main>
      </div>
    </div>
  `;

  document.getElementById("userLabel").textContent =
    `${currentUser.full_name} · ${currentUser.role}`;

  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      loadPage(btn.dataset.page);
    });
  });

  loadPage("dashboard");
}

async function loadPage(page) {
  try {
    if (page === "dashboard") await dashboard();
    if (page === "customers") await customers();
    if (page === "people") await serviceForm("people");
    if (page === "objects") await serviceForm("objects");
    if (page === "records") await records();
    if (page === "employees") await employees();
  } catch (error) {
    document.getElementById("content").innerHTML =
      `<div class="error">${escapeHtml(error.message)}</div>`;
  }
}

async function dashboard() {
  const d = await api("/dashboard");

  document.getElementById("content").innerHTML = `
    <h1>Dashboard</h1>
    <p class="muted">Today · 24 / 7 operation</p>

    <div class="cards">
      <div class="card">
        <div class="muted">PEOPLE</div>
        <div class="number">${d.people}</div>
      </div>
      <div class="card">
        <div class="muted">OBJECTS</div>
        <div class="number">${d.objects}</div>
      </div>
      <div class="card">
        <div class="muted">TOTAL</div>
        <div class="number">${d.total}</div>
      </div>
      <div class="card">
        <div class="muted">PENDING PAYMENTS</div>
        <div class="number">${d.pending_payments}</div>
      </div>
    </div>

    <div class="actions">
      <button class="primary" onclick="loadPage('people')">NEW PEOPLE SERVICE</button>
      <button class="secondary" onclick="loadPage('objects')">NEW OBJECT SERVICE</button>
      <button class="secondary" onclick="loadPage('customers')">CUSTOMERS</button>
    </div>

    <div class="form-card">
      <h3>Operating principle</h3>
      <p class="muted">
        Employees register the service and payment information.
        The system does not provide GPS package tracking and has no chatbot.
      </p>
    </div>
  `;
}

async function customers() {
  const data = await api("/customers");

  document.getElementById("content").innerHTML = `
    <h1>Customers</h1>

    <form class="form-card" id="customerForm">
      <div class="grid2">
        <div>
          <label>Full name</label>
          <input id="cName" required>
        </div>
        <div>
          <label>Phone</label>
          <input id="cPhone">
        </div>
        <div>
          <label>Email</label>
          <input id="cEmail" type="email">
        </div>
        <div>
          <label>Notes</label>
          <input id="cNotes">
        </div>
      </div>
      <br>
      <button class="primary">SAVE CUSTOMER</button>
    </form>

    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>Name</th><th>Phone</th><th>Email</th><th>Notes</th></tr></thead>
        <tbody>
          ${data.map(c => `
            <tr>
              <td>${c.id}</td>
              <td>${escapeHtml(c.full_name)}</td>
              <td>${escapeHtml(c.phone)}</td>
              <td>${escapeHtml(c.email)}</td>
              <td>${escapeHtml(c.notes)}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;

  document.getElementById("customerForm").addEventListener("submit", async e => {
    e.preventDefault();

    await api("/customers", {
      method: "POST",
      body: JSON.stringify({
        full_name: document.getElementById("cName").value,
        phone: document.getElementById("cPhone").value || null,
        email: document.getElementById("cEmail").value || null,
        notes: document.getElementById("cNotes").value || null
      })
    });

    customers();
  });
}

async function serviceForm(type) {
  const customers = await api("/customers");
  const title = type === "people" ? "People transportation" : "Object transportation";

  document.getElementById("content").innerHTML = `
    <h1>${title}</h1>
    <p class="muted">Register a new service.</p>

    ${customers.length === 0
      ? `<div class="form-card">
           <p>No customers exist yet.</p>
           <button class="primary" onclick="loadPage('customers')">CREATE CUSTOMER FIRST</button>
         </div>`
      : `
      <form class="form-card" id="serviceForm">
        <div class="grid2">
          <div>
            <label>Customer</label>
            <select id="sCustomer" required>
              ${customers.map(c => `<option value="${c.id}">${escapeHtml(c.full_name)} · ${escapeHtml(c.phone)}</option>`).join("")}
            </select>
          </div>

          <div>
            <label>Date</label>
            <input id="sDate" type="date" required>
          </div>

          <div>
            <label>Time</label>
            <input id="sTime" type="time" required>
          </div>

          <div>
            <label>Price</label>
            <input id="sPrice" type="number" min="0" step="0.01" value="0" required>
          </div>

          <div>
            <label>Origin</label>
            <input id="sOrigin" required>
          </div>

          <div>
            <label>Destination</label>
            <input id="sDestination" required>
          </div>

          ${type === "people" ? `
            <div>
              <label>Passengers</label>
              <input id="sPassengers" type="number" min="1" value="1" required>
            </div>
          ` : `
            <div>
              <label>Object description</label>
              <input id="sObject" required>
            </div>
            <div>
              <label>Quantity</label>
              <input id="sQuantity" type="number" min="1" value="1" required>
            </div>
          `}

          <div>
            <label>Status</label>
            <select id="sStatus">
              <option value="pending">Pending</option>
              <option value="scheduled">Scheduled</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        <label>Notes</label>
        <textarea id="sNotes"></textarea>

        <br>
        <button class="primary">SAVE SERVICE</button>
      </form>
    `}

    <div class="form-card">
      <h3>Important</h3>
      <p class="muted">
        The employee records the service. There is no automatic package GPS tracking.
        Payment is recorded separately and can be marked as paid face-to-face.
      </p>
    </div>
  `;

  const form = document.getElementById("serviceForm");
  if (!form) return;

  const now = new Date();
  document.getElementById("sDate").value = now.toISOString().slice(0, 10);
  document.getElementById("sTime").value =
    now.toTimeString().slice(0, 5);

  form.addEventListener("submit", async e => {
    e.preventDefault();

    const payload = {
      customer_id: Number(document.getElementById("sCustomer").value),
      service_type: type,
      origin: document.getElementById("sOrigin").value,
      destination: document.getElementById("sDestination").value,
      service_date: document.getElementById("sDate").value,
      service_time: document.getElementById("sTime").value,
      price: Number(document.getElementById("sPrice").value),
      status: document.getElementById("sStatus").value,
      notes: document.getElementById("sNotes").value || null
    };

    if (type === "people") {
      payload.passengers = Number(document.getElementById("sPassengers").value);
    } else {
      payload.object_description = document.getElementById("sObject").value;
      payload.quantity = Number(document.getElementById("sQuantity").value);
    }

    await api("/services", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    alert("Service created.");
    loadPage("records");
  });
}

async function records() {
  const data = await api("/services");

  document.getElementById("content").innerHTML = `
    <h1>Service records</h1>
    <p class="muted">${data.length} registered services</p>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Customer</th>
            <th>Route</th>
            <th>Date</th>
            <th>Employee</th>
            <th>Price</th>
            <th>Status</th>
            <th>Payment</th>
          </tr>
        </thead>
        <tbody>
          ${data.map(s => `
            <tr>
              <td>${s.id}</td>
              <td>${s.service_type}</td>
              <td>${escapeHtml(s.customer_name)}</td>
              <td>${escapeHtml(s.origin)} → ${escapeHtml(s.destination)}</td>
              <td>${s.service_date} ${String(s.service_time).slice(0,5)}</td>
              <td>${escapeHtml(s.employee_name)}</td>
              <td>$${Number(s.price).toLocaleString()}</td>
              <td><span class="badge">${escapeHtml(s.status)}</span></td>
              <td>
                ${s.payment_status === "paid"
                  ? `<span class="success">PAID</span>`
                  : `<button class="secondary" onclick="markPaid(${s.id}, ${Number(s.price)})">MARK PAID</button>`}
              </td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

async function markPaid(serviceId, amount) {
  await api(`/services/${serviceId}/payment`, {
    method: "POST",
    body: JSON.stringify({
      amount,
      payment_method: "cash",
      payment_status: "paid"
    })
  });

  records();
}

async function employees() {
  const data = await api("/employees");

  document.getElementById("content").innerHTML = `
    <h1>Employees</h1>
    <p class="muted">8 employee accounts. Passwords are stored only as secure hashes.</p>

    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>Username</th><th>Name</th><th>Role</th><th>Active</th></tr></thead>
        <tbody>
          ${data.map(e => `
            <tr>
              <td>${e.id}</td>
              <td>${escapeHtml(e.username)}</td>
              <td>${escapeHtml(e.full_name)}</td>
              <td>${escapeHtml(e.role)}</td>
              <td>${e.active ? '<span class="success">YES</span>' : 'NO'}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

async function boot() {
  if (!token) {
    renderLogin();
    return;
  }

  try {
    currentUser = await api("/me");
    renderApp();
  } catch {
    logout();
  }
}

boot();
'''

files["README.md"] = r'''
# Transport24

Small 24/7 transportation management application for people and objects.

## Stack

- FastAPI / Python
- PostgreSQL
- HTML/CSS/JavaScript
- Docker Compose
- JWT authentication
- Argon2 password hashing

## Features

- 8 employee accounts
- Employee login
- Customer records
- People transportation services
- Object transportation services
- Service records
- Face-to-face cash payment recording
- Dashboard
- No chatbot
- No GPS package tracking
- Dark gray / black / blue terminal-style UI

## Run

Requirements:

- Docker
- Docker Compose

From this directory:

```bash
docker compose up -d --build
