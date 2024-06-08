from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
import sqlite3

router = APIRouter()

# Pydantic model for RiwayatPendidikan data
class RiwayatPendidikan(BaseModel):
    id_riwayat_pend_dokter: int
    S1: str | None = None
    S2: str | None = None
    S3: str | None = None

@router.get("/init/", status_code=status.HTTP_201_CREATED)
def init_db():
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS RiwayatPendidikan")  # Drop the existing table if it exists
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS RiwayatPendidikan (
                id_riwayat_pend_dokter INTEGER PRIMARY KEY AUTOINCREMENT,
                S1 TEXT,
                S2 TEXT,
                S3 TEXT
            )"""
        )
        conn.commit()
    except Exception as e:
        return {"status": f"Error saat membuat tabel: {e}"}
    finally:
        conn.close()
    return {"status": "Berhasil membuat tabel Riwayat Pendidikan"}

@router.post("/addRiwayatPendidikan", status_code=status.HTTP_201_CREATED)
def add_riwayat_pendidikan(riwayat_pendidikan: RiwayatPendidikan):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO RiwayatPendidikan (id_riwayat_pend_dokter, S1, S2, S3)
            VALUES (?, ?, ?, ?)""",
            (riwayat_pendidikan.id_riwayat_pend_dokter, riwayat_pendidikan.S1, riwayat_pendidikan.S2, riwayat_pendidikan.S3)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Error adding riwayat pendidikan")
    finally:
        conn.close()
    return {"message": "Riwayat pendidikan added successfully"}

@router.get("/getRiwayatPendidikan/{id_riwayat_pend_dokter}", status_code=status.HTTP_200_OK)
def get_riwayat_pendidikan(id_riwayat_pend_dokter: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM RiwayatPendidikan WHERE id_riwayat_pend_dokter = ?", (id_riwayat_pend_dokter,))
    riwayat = cursor.fetchall()
    conn.close()
    if riwayat:
        return [
            {
                "id_riwayat_pend_dokter": pendidikan[0],
                "S1": pendidikan[1],
                "S2": pendidikan[2],
                "S3": pendidikan[3],
            }
            for pendidikan in riwayat
        ]
    raise HTTPException(status_code=404, detail="No riwayat pendidikan found")
