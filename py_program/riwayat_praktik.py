from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
import sqlite3

router = APIRouter()

# Pydantic model for RiwayatPraktik data
class RiwayatPraktik(BaseModel):
    id_riwayat_praktik_dokter: int
    Tempat1: str | None = None
    Tempat2: str | None = None
    Tempat3: str | None = None

@router.get("/init/", status_code=status.HTTP_201_CREATED)
def init_db():
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS RiwayatPraktik")  # Drop the existing table if it exists
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS RiwayatPraktik (
                id_riwayat_praktik_dokter INTEGER PRIMARY KEY AUTOINCREMENT,
                Tempat1 TEXT,
                Tempat2 TEXT,
                Tempat3 TEXT
            )"""
        )
        conn.commit()
    except Exception as e:
        return {"status": f"Error saat membuat tabel: {e}"}
    finally:
        conn.close()
    return {"status": "Berhasil membuat tabel Riwayat Praktik"}

@router.post("/addRiwayatPraktik", status_code=status.HTTP_201_CREATED)
def add_riwayat_Praktik(riwayat_Praktik: RiwayatPraktik):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO RiwayatPraktik (id_riwayat_praktik_dokter, Tempat1, Tempat2, Tempat3)
            VALUES (?, ?, ?, ?)""",
            (riwayat_Praktik.id_riwayat_praktik_dokter, riwayat_Praktik.Tempat1, riwayat_Praktik.Tempat2, riwayat_Praktik.Tempat3)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Error adding riwayat Praktik")
    finally:
        conn.close()
    return {"message": "Riwayat Praktik added successfully"}

@router.get("/getRiwayatPraktik/{id_riwayat_praktik_dokter}", status_code=status.HTTP_200_OK)
def get_riwayat_Praktik(id_riwayat_praktik_dokter: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM RiwayatPraktik WHERE id_riwayat_praktik_dokter = ?", (id_riwayat_praktik_dokter,))
    riwayat = cursor.fetchall()
    conn.close()
    if riwayat:
        return [
            {
                "id_riwayat_praktik_dokter": praktik[0],
                "Tempat1": praktik[1],
                "Tempat2": praktik[2],
                "Tempat3": praktik[3],
            }
            for praktik in riwayat
        ]
    raise HTTPException(status_code=404, detail="No riwayat Praktik found")
