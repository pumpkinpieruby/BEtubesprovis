from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
import sqlite3

router = APIRouter()

# Pydantic model for medicine data
class Obat(BaseModel):
    id_obat: int
    nama_obat: str
    harga_obat: str

@router.get("/init/", status_code=status.HTTP_201_CREATED)
def init_db():
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Obat (
                id_obat INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_obat TEXT NOT NULL,
                harga_obat TEXT NOT NULL
            )"""
        )
        conn.commit()
    except Exception as e:
        return {"status": f"Error saat membuat tabel: {e}"}
    finally:
        conn.close()
    return {"status": "Berhasil membuat tabel Obat"}


@router.post("/addObat", status_code=status.HTTP_201_CREATED)
def add_obat(obat: Obat):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO Obat (nama_obat, harga_obat)
            VALUES (?, ?)""",
            (obat.nama_obat, obat.harga_obat)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Error adding obat")
    finally:
        conn.close()
    return {"message": "Obat added successfully"}

@router.get("/getObat/{id_obat}", status_code=status.HTTP_200_OK)
def get_obat(id_obat: int):
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Obat WHERE obat_id = ?", (id_obat,))
        obat = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

    if obat:
        return {
            "id_obat": obat[0],
            "nama_obat": obat[1],
            "harga_obat": obat[2],
        }
    else:
        raise HTTPException(status_code=404, detail="Obat not found")