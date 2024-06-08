from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Response
from typing import List 
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

class UserPatch(BaseModel):
    user_password: str | None = "kosong"

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


@router.get('/getAllUsers', response_model=List[User])
def get_all_users():
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    conn.close()
    if users:
        return [
            {
                "user_nama": user[1],
                "user_email": user[2],
                "user_no_telp": user[3],
                "user_password": user[4],
                "user_nik": user[5],
                "user_tanggal_lahir": user[6],
                "user_bpjs": user[7],
            }
            for user in users
        ]
    raise HTTPException(status_code=404, detail="No users found")

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

@router.patch("/update_user/{user_id}",response_model=UserPatch)
def update_user(response: Response, user_id: int, u: UserPatch):
    try:
        print(str(u))
        DB_NAME = "carewave.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("select * from user where user_id = ?", (user_id,))  # tambah koma untuk menandakan tupple
        existing_item = cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))
    if existing_item:  # data ada, lakukan update
        # asumsi minimal ada satu field update
        # todo: bisa di-refactor dan dirapikan
        sqlstr = "UPDATE user SET "
        if u.user_password != "kosong":
            if u.user_password is not None:
                sqlstr += "user_password = '{}', ".format(u.user_password)
            else:
                sqlstr += "user_password = NULL, "        
        sqlstr = sqlstr[:-2]  # Remove the trailing comma and space
        
        sqlstr += " WHERE user_id = {}".format(user_id)
        print(sqlstr)
        print("ssssss")
        try:
            cur.execute(sqlstr)
            con.commit()
            response.headers["location"] = "/user/{}".format(user_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception:  {}".format(str(e)))
    else:  # data tidak ada 404, item not found
        raise HTTPException(status_code=404, detail="Item Not Found")
    con.close()
    return u