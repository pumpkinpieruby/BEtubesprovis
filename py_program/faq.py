from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
import sqlite3

router = APIRouter()

# Pydantic model for FAQ data
class FAQ(BaseModel):
    id_faq: int
    judul_faq: str
    deskripsi_faq: str

# Init db for FAQ
@router.get("/init/", status_code=status.HTTP_201_CREATED)
def init_db():
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS Faq")  # Drop the existing table if it exists
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Faq(
                id_faq INTEGER PRIMARY KEY AUTOINCREMENT,
                judul_faq TEXT NOT NULL,
                deskripsi_faq TEXT NOT NULL
            )"""
        )
        conn.commit()
    except Exception as e:
        return {"status": f"Error saat membuat tabel: {e}"}
    finally:
        conn.close()
    return {"status": "Berhasil membuat tabel FAQ"}

@router.post("/addFAQ", status_code=status.HTTP_201_CREATED)
def add_faq(faq: FAQ):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO Faq (id_faq, judul_faq, deskripsi_faq)
            VALUES (?, ?, ?)""",
            (faq.id_faq, faq.judul_faq, faq.deskripsi_faq)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Integrity error adding faq")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        conn.close()
    return {"message": "FAQ added successfully"}

@router.get("/getFAQ/{id_faq}", status_code=status.HTTP_200_OK)
def get_faq(id_faq: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Faq WHERE id_faq = ?", (id_faq,))
        faq = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        conn.close()

    if faq:
        return {
            "id_faq": faq[0],
            "judul_faq": faq[1],
            "deskripsi_faq": faq[2],
        }
    raise HTTPException(status_code=404, detail="FAQ not found")
