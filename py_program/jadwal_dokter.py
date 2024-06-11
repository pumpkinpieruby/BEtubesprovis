from fastapi import APIRouter, HTTPException, status, Path
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

router = APIRouter()

# Pydantic model for JadwalDokter
class JadwalDokter(BaseModel):
    id_jadwal_dokter: Optional[int] = None
    hari: str
    jam_masuk: str
    jam_selesai: str
    id_doctor: int

# @router.get("/init/", status_code=status.HTTP_201_CREATED)
# def init_db():
#     try:
#         conn = sqlite3.connect("carewave.db")
#         cursor = conn.cursor()
#         cursor.execute("DROP TABLE IF EXISTS JadwalDokter")  # Drop the existing table if it exists
#         cursor.execute(
#             """CREATE TABLE IF NOT EXISTS JadwalDokter (
#                 id_jadwal_dokter INTEGER PRIMARY KEY AUTOINCREMENT,
#                 hari TEXT,
#                 jam_masuk TEXT,
#                 jam_selesai TEXT,
#                 id_doctor INTEGER,
#                 FOREIGN KEY (id_doctor) REFERENCES Doctor (id_doctor)
#                 )"""
#         )
#         conn.commit()
#     except Exception as e:
#         return {"status": f"Error saat membuat tabel: {e}"}
#     finally:
#         conn.close()
#     return {"status": "Berhasil membuat tabel Doctor"}

# Menambahkan jadwal dokter
@router.post("/", status_code=status.HTTP_201_CREATED)
def add_jadwal_dokter(jadwal_dokter: JadwalDokter):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO JadwalDokter (hari, jam_masuk, jam_selesai, id_doctor)
            VALUES (?, ?, ?, ?)""",
            (jadwal_dokter.hari, jadwal_dokter.jam_masuk, jadwal_dokter.jam_selesai, jadwal_dokter.id_doctor)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Error adding jadwal dokter")
    finally:
        conn.close()
    return {"message": "Jadwal dokter added successfully"}

# Mendapatkan semua jadwal dokter
@router.get("/getAllJadwal", response_model=List[JadwalDokter], status_code=status.HTTP_200_OK)
def get_all_jadwal():
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT j.id_jadwal_dokter, j.hari, j.jam_masuk, j.jam_selesai, j.id_doctor
        FROM JadwalDokter j
        JOIN Doctor d ON j.id_doctor = d.id_doctor
    """)
    jadwal = cursor.fetchall()
    conn.close()
    if jadwal:
        return [
            {
                "id_jadwal_dokter": j[0],
                "hari": j[1],
                "jam_masuk": j[2],
                "jam_selesai": j[3],
                "id_doctor": j[4]
            }
            for j in jadwal
        ]
    raise HTTPException(status_code=404, detail="No schedules found")

# Mendapatkan jadwal dokter berdasarkan ID
@router.get("/getJadwalByDoctor/{id_doctor}", response_model=List[JadwalDokter], status_code=status.HTTP_200_OK)
def get_jadwal_by_doctor(id_doctor: int = Path(..., title="The ID of the doctor to get schedules for", ge=1)):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT j.id_jadwal_dokter, j.hari, j.jam_masuk, j.jam_selesai, j.id_doctor FROM JadwalDokter j JOIN Doctor d ON j.id_doctor = d.id_doctor WHERE j.id_doctor = ?", (id_doctor,))
    jadwal = cursor.fetchall()
    conn.close()
    if jadwal:
        return [
            {
                "id_jadwal_dokter": j[0],
                "hari": j[1],
                "jam_masuk": j[2],
                "jam_selesai": j[3],
                "id_doctor": j[4]
            }
            for j in jadwal
        ]
    raise HTTPException(status_code=404, detail="No schedules found")

# Memperbarui jadwal dokter
@router.put("/{id_jadwal_dokter}", response_model=JadwalDokter, status_code=status.HTTP_200_OK)
def update_jadwal_dokter(jadwal_dokter: JadwalDokter, id_jadwal_dokter: int = Path(..., title="The ID of the jadwal dokter to update", ge=1)):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """UPDATE JadwalDokter
            SET hari = ?, jam_masuk = ?, jam_selesai = ?, id_doctor = ?
            WHERE id_jadwal_dokter = ?""",
            (jadwal_dokter.hari, jadwal_dokter.jam_masuk, jadwal_dokter.jam_selesai, jadwal_dokter.id_doctor, id_jadwal_dokter)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Error updating jadwal dokter")
    finally:
        conn.close()
    return jadwal_dokter

# Menghapus jadwal dokter
@router.delete("/{id_jadwal_dokter}", status_code=status.HTTP_200_OK)
def delete_jadwal_dokter(id_jadwal_dokter: int = Path(..., title="The ID of the jadwal dokter to delete", ge=1)):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM JadwalDokter WHERE id_jadwal_dokter = ?", (id_jadwal_dokter,))
    conn.commit()
    conn.close()
    return {"message": "Jadwal dokter deleted successfully"}
