from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import sqlite3

router = APIRouter()

# Pydantic model for laboratory check data
class CheckLab(BaseModel):
    user_id: str
    jenis_ceklab: str
    foto: str  # Mengubah tipe data foto menjadi string biasa
    tanggal: str



# Function to initialize database and create ceklab table
@router.get("/init_db/")
def init_db():
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS ceklab(
                Ceklab_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                jenis_ceklab TEXT NOT NULL,
                foto TEXT NOT NULL,
                tanggal TEXT NOT NULL
            )"""
        )
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing database: {e}")
    finally:
        conn.close()
    return {"message": "Database initialized successfully and ceklab table created"}


# Database connection function
def connect_db():
    try:
        conn = sqlite3.connect("carewave.db")
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to database: {e}")

# Helper function to insert laboratory check data
def insert_checklab(checklab: CheckLab):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Insert the laboratory check data into the database
        cursor.execute(
            """INSERT INTO ceklab (user_id, jenis_ceklab, foto, tanggal)
            VALUES (?, ?, ?, ?)""",
            (checklab.user_id, checklab.jenis_ceklab, checklab.foto, checklab.tanggal)  # Menggunakan foto langsung dari model
        )
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting check data into database: {e}")
    finally:
        conn.close()

# Endpoint to add new laboratory check data
@router.post("/add_checklab/")
def add_checklab(checklab: CheckLab):
    insert_checklab(checklab)
    return {"message": "Laboratory check data added successfully"}

@router.get("/getchecklab/", response_model=list[CheckLab])
def getchecklab():
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, jenis_ceklab, foto, tanggal FROM ceklab")
        records = cursor.fetchall()
        if records:
            return [
                {
                    "user_id": record[0],
                    "jenis_ceklab": record[1],
                    "foto": record[2],
                    "tanggal": record[3],
                }
                for record in records
            ]
        else:
            raise HTTPException(status_code=404, detail="No laboratory check data found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving check data from database: {e}")
    finally:
        conn.close()
