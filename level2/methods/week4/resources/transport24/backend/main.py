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
