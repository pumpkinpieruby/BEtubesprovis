from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
import sqlite3

router = APIRouter()

# Pydantic model for registration data
class Pendaftaran(BaseModel):
    user_id: int
    dokter_id: int
    tanggal: str
    jam: str
    hari: str  # Menambahkan atribut hari

# Init db for pendaftaran
@router.get("/init_pendaftaran/", status_code=status.HTTP_201_CREATED)
def init_db_pendaftaran():
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS pendaftaran (
                id_pendaftaran INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                dokter_id INTEGER NOT NULL,
                tanggal TEXT NOT NULL,
                jam TEXT NOT NULL,
                hari TEXT NOT NULL,  -- Menambahkan kolom untuk hari
                FOREIGN KEY (user_id) REFERENCES user (user_id),
                FOREIGN KEY (dokter_id) REFERENCES dokter (dokter_id)
            )"""
        )
        conn.commit()
    except Exception as e:
        return {"status": f"Error saat membuat tabel: {e}"}
    finally:
        conn.close()
    return {"status": "Berhasil membuat tabel pendaftaran"}

# Adding registration
@router.post("/addPendaftaran", status_code=status.HTTP_201_CREATED)
def add_pendaftaran(pendaftaran: Pendaftaran):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO pendaftaran (user_id, dokter_id, tanggal, jam, hari)
            VALUES (?, ?, ?, ?, ?)""",
            (pendaftaran.user_id, pendaftaran.dokter_id, pendaftaran.tanggal, pendaftaran.jam, pendaftaran.hari)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Error adding registration")
    finally:
        conn.close()
    return {"message": "Registration added successfully"}

# Getting all registrations for a user
@router.get("/getPendaftaran/{user_id}", status_code=status.HTTP_200_OK)
def get_pendaftaran(user_id: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pendaftaran WHERE user_id = ?", (user_id,))
    registrations = cursor.fetchall()
    conn.close()
    if registrations:
        return [
            {
                "id_pendaftaran": registration[0],
                "user_id": registration[1],
                "dokter_id": registration[2],
                "tanggal": registration[3],
                "jam": registration[4],
                "hari": registration[5],  # Menambahkan atribut hari
            }
            for registration in registrations
        ]
    raise HTTPException(status_code=404, detail="No registrations found")
