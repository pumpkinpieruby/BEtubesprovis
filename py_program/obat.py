from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
import sqlite3

router = APIRouter()

class Obat(BaseModel):
    id_obat: int
    nama_obat: str
    harga_obat: str

@router.post("/addObat", status_code=status.HTTP_201_CREATED)
def add_obat(obat: Obat):
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
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

@router.get("/getObat/{id_obat}", response_model=Obat, status_code=status.HTTP_200_OK)
def get_obat(id_obat: int):
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Obat WHERE id_obat = ?", (id_obat,))
        obat = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        conn.close()

    if obat:
        return {
            "id_obat": obat[0],
            "nama_obat": obat[1],
            "harga_obat": obat[2]
        }
    else:
        raise HTTPException(status_code=404, detail="Obat not found")

@router.get("/getAllObat", response_model=List[Obat], status_code=status.HTTP_200_OK)
def get_all_obat():
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Obat")
    obats = cursor.fetchall()
    conn.close()
    if obats:
        return [
            {
                "id_obat": obat[0],
                "nama_obat": obat[1],
                "harga_obat": obat[2]
            }
            for obat in obats
        ]
    raise HTTPException(status_code=404, detail="No obats found")
