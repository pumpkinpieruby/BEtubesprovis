from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
import sqlite3

router = APIRouter()

class ResepObat(BaseModel):
    id_resep_obat: int
    id_obat: int
    id_pendaftaran: int
    deskripsi: str

@router.post("/addResepObat", status_code=status.HTTP_201_CREATED)
def add_resep_obat(resep_obat: ResepObat):
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO ResepObat (id_obat, id_pendaftaran, deskripsi)
            VALUES (?, ?, ?)""",
            (resep_obat.id_obat, resep_obat.id_pendaftaran, resep_obat.deskripsi)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Error adding resep obat")
    finally:
        conn.close()
    return {"message": "Resep obat added successfully"}

@router.get("/getResepObat/{id_resep_obat}", response_model=ResepObat, status_code=status.HTTP_200_OK)
def get_resep_obat(id_resep_obat: int):
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ResepObat WHERE id_resep_obat = ?", (id_resep_obat,))
        resep_obat = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

    if resep_obat:
        return {
            "id_resep_obat": resep_obat[0],
            "id_obat": resep_obat[1],
            "id_pendaftaran": resep_obat[2],
            "deskripsi": resep_obat[3]
        }
    else:
        raise HTTPException(status_code=404, detail="Resep obat not found")

@router.get("/getAllResepObat", response_model=List[ResepObat], status_code=status.HTTP_200_OK)
def get_all_resep_obat():
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ResepObat")
    resep_obats = cursor.fetchall()
    conn.close()
    if resep_obats:
        return [
            {
                "id_resep_obat": ro[0],
                "id_obat": ro[1],
                "id_pendaftaran": ro[2],
                "deskripsi": ro[3]
            }
            for ro in resep_obats
        ]
    raise HTTPException(status_code=404, detail="No resep obats found")
