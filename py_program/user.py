from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import sqlite3


router = APIRouter()

# Pydantic models for user data
class User(BaseModel):
    user_nama: str
    user_email: str
    user_no_telp: str
    user_password: str
    user_nik: str
    user_tanggal_lahir: str
    user_bpjs: str

#init db
@router.get("/init/")
def init_db():
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute(
            """ CREATE TABLE IF NOT EXISTS user(
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_nama TEXT NOT NULL,
                user_email TEXT NOT NULL UNIQUE,
                user_no_telp TEXT NOT NULL,
                user_password TEXT NOT NULL,
                user_nik TEXT NOT NULL,
                user_tanggal_lahir TEXT NOT NULL,
                user_bpjs TEXT NOT NULL)"""
        )
        conn.commit()
    except Exception as e:
        return {"status": f"Error saat membuat tabel User: {e}"}
    finally:
        conn.close()
    return {"status": "Berhasil membuat tabel User"}


@router.get('/getAllUsers')
def get_user():
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user")
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            "user_nama": user[1],
            "user_email": user[2],
            "user_no_telp": user[3],
            "user_password": user[4],
            "user_nik": user[5],
            "user_tanggal_lahir": user[6],
            "user_bpjs": user[7],
        }
    return None

# User registration
@router.post("/register")
def register_user(user: User):
    
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO user (user_nama, user_email, user_no_telp, user_password, user_nik, user_tanggal_lahir, user_bpjs)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user.user_nama, user.user_email, user.user_no_telp, user.user_password, user.user_nik, user.user_tanggal_lahir, user.user_bpjs)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        conn.close()
    return {"message": "User registered successfully"}

# User login validation
@router.get("/login/{email}/{password}")
def validator_login(email: str, password: str):
    try:
        DB_NAME = "carewave.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            """
            SELECT *
            FROM user
            WHERE user_email = ? AND user_password = ?
        """, (email, password,))
        existing_item = cur.fetchone()
    except:
        return ({"status": "terjadi error"})
    finally:
        con.close()
    if existing_item:
        return ["Ada", existing_item[1], existing_item[2]]
    else:
        return ["Tidak Ada"]

