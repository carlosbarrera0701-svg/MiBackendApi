import sqlite3
import random
import string
import time
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, EmailStr

# Inicializar la app
app = FastAPI(title="Backend Auth & Gemini API", version="1.0")

DB_NAME = "users.db"

# ==========================================
# 1. BASE DE DATOS
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Tabla de códigos de verificación
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            expires_at REAL NOT NULL,
            is_used INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

# Crear las tablas al arrancar el script
init_db()

# ==========================================
# 2. MODELOS (SCHEMAS JSON)
# ==========================================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

# ==========================================
# 3. HELPER DE ENVIAR CORREO (O IMPRIMIR)
# ==========================================
def enviar_codigo(email: str, code: str):
    # Por ahora imprimimos en consola para que pruebes fácil.
    # Cuando quieras usar correo real, aquí configuras smtplib.
    print(f"\n==========================================")
    print(f"📩 CÓDIGO ENVIADO A {email}: {code}")
    print(f"==========================================\n")

# ==========================================
# 4. ENDPOINTS DE AUTENTICACIÓN
# ==========================================

# PASO 1: Validar credenciales y enviar código
@app.post("/api/v1/auth/login-request")
def login_request(data: LoginRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Validar que el usuario exista y la contraseña sea correcta
    pass_hash = hashlib.sha256(data.password.encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE email = ? AND password_hash = ?", (data.email, pass_hash))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    # Generar código numérico de 6 dígitos
    code = ''.join(random.choices(string.digits, k=6))
    expires_at = time.time() + (10 * 60)  # Expira en 10 min

    # Guardar en la BD
    cursor.execute(
        "INSERT INTO verification_codes (email, code, expires_at) VALUES (?, ?, ?)",
        (data.email, code, expires_at)
    )
    conn.commit()
    conn.close()

    # Manda / Imprime el código
    enviar_codigo(data.email, code)

    return {
        "status": "ok",
        "message": "Credenciales correctas. Código enviado."
    }

# PASO 2: Validar el código ingresado
@app.post("/api/v1/auth/verify-code")
def verify_code(data: VerifyCodeRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, expires_at, is_used FROM verification_codes WHERE email = ? AND code = ? ORDER BY id DESC LIMIT 1",
        (data.email, data.code)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="Código inválido")

    code_id, expires_at, is_used = row

    if is_used == 1:
        conn.close()
        raise HTTPException(status_code=400, detail="Este código ya fue utilizado")

    if time.time() > expires_at:
        conn.close()
        raise HTTPException(status_code=400, detail="El código ya expiró")

    conn.close()
    return {"status": "ok", "message": "Código válido"}

# PASO 3: Cambiar la contraseña
@app.post("/api/v1/auth/change-password")
def change_password(data: ResetPasswordRequest):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Validar que el código sirva
    cursor.execute(
        "SELECT id, expires_at, is_used FROM verification_codes WHERE email = ? AND code = ? ORDER BY id DESC LIMIT 1",
        (data.email, data.code)
    )
    row = cursor.fetchone()

    if not row or row[2] == 1 or time.time() > row[1]:
        conn.close()
        raise HTTPException(status_code=400, detail="Código inválido o expirado")

    code_id = row[0]

    # Actualizar la contraseña en el usuario
    new_hash = hashlib.sha256(data.new_password.encode()).hexdigest()
    cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, data.email))

    # Quemas el código para que no lo usen 2 veces
    cursor.execute("UPDATE verification_codes SET is_used = 1 WHERE id = ?", (code_id,))

    conn.commit()
    conn.close()

    return {"status": "ok", "message": "Contraseña actualizada exitosamente"}