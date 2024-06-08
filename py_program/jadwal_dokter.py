# routers/jadwal_dokter.py
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
import sqlite3

router = APIRouter()

# Pydantic model for JadwalDokter data
class JadwalDokter(BaseModel):
    id_jadwal_dokter: int
    hari: str
    jam_masuk: str
    jam_selesai: str

@router.get("/init/", status_code=status.HTTP_201_CREATED)
def init_db():
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS JadwalDokter (
                id_jadwal_dokter INTEGER PRIMARY KEY AUTOINCREMENT,
                hari TEXT NOT NULL,
                jam_masuk TEXT NOT NULL,
                jam_selesai TEXT NOT NULL
            )"""
        )
        conn.commit()
    except Exception as e:
        return {"status": f"Error saat membuat tabel: {e}"}
    finally:
        conn.close()
    return {"status": "Berhasil membuat tabel Jadwal Dokter"}

@router.post("/addJadwalDokter", status_code=status.HTTP_201_CREATED)
def add_jadwal_dokter(jadwal_dokter: JadwalDokter):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO JadwalDokter (id_jadwal_dokter, hari, jam_masuk, jam_selesai)
            VALUES (?, ?, ?, ?)""",
            (jadwal_dokter.id_jadwal_dokter, jadwal_dokter.hari, jadwal_dokter.jam_masuk, jadwal_dokter.jam_selesai)
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Error adding jadwal dokter: {e}")
    finally:
        conn.close()
    return {"message": "Jadwal dokter added successfully"}

@router.get("/getJadwalDokter/{id_jadwal_dokter}", status_code=status.HTTP_200_OK)
def get_jadwal_dokter(id_jadwal_dokter: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM JadwalDokter WHERE id_jadwal_dokter = ?", (id_jadwal_dokter,))
    jadwal = cursor.fetchall()
    conn.close()
    if jadwal:
        return [
            {
                "id_jadwal_dokter": jadwalDokter[0],
                "hari": jadwalDokter[1],
                "jam_masuk": jadwalDokter[2],
                "jam_selesai": jadwalDokter[3],
            }
            for jadwalDokter in jadwal
        ]
    raise HTTPException(status_code=404, detail="No jadwal dokter found")
