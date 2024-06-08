from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
import sqlite3


router = APIRouter()

# Pydantic model for doctor data
class Doctor(BaseModel):
    id_doctor: int
    doctor_name: str
    doctor_spesialist: str
    doctor_STR: str
    doctor_price: str
    id_jadwal_dokter: int
    id_riwayat_pendidikan_dokter: int
    id_riwayat_praktik_dokter: int

class JadwalDokter(BaseModel):
    id_jadwal_dokter: int
    hari: str
    jam_masuk: str
    jam_selesai: str

class RiwayatPendidikan(BaseModel):
    id_riwayat_pend_dokter: int
    S1: str | None = None
    S2: str | None = None
    S3: str | None = None

class RiwayatPraktik(BaseModel):
    id_riwayat_praktik_dokter: int
    Tempat1: str | None = None
    Tempat2: str | None = None
    Tempat3: str | None = None
    
    
# Init db for doctor
@router.get("/init/", status_code=status.HTTP_201_CREATED)
def init_db():
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS Doctor")  # Drop the existing table if it exists
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Doctor(
                id_doctor INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_name TEXT NOT NULL,
                doctor_spesialist TEXT NOT NULL,
                doctor_STR TEXT NOT NULL,
                doctor_price TEXT NOT NULL,
                id_jadwal_dokter INTEGER NOT NULL,
                id_riwayat_pendidikan_dokter INTEGER NOT NULL,
                id_riwayat_praktik_dokter INTEGER NOT NULL,
                FOREIGN KEY (id_jadwal_dokter) REFERENCES JadwalDokter(id_jadwal_dokter),
                FOREIGN KEY (id_riwayat_pendidikan_dokter) REFERENCES RiwayatPendidikanDokter(id_riwayat_pendidikan_dokter),
                FOREIGN KEY (id_riwayat_praktik_dokter) REFERENCES RiwayatPraktikDokter(id_riwayat_praktik_dokter)
            )"""
        )
        conn.commit()
    except Exception as e:
        return {"status": f"Error saat membuat tabel: {e}"}
    finally:
        conn.close()
    return {"status": "Berhasil membuat tabel Doctor"}
@router.post("/addDoctor", status_code=status.HTTP_201_CREATED)


def add_doctor(doctor: Doctor):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO Doctor (id_doctor, doctor_name, doctor_spesialist, doctor_STR, doctor_price, id_jadwal_dokter, id_riwayat_pendidikan_dokter, id_riwayat_praktik_dokter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (doctor.id_doctor, doctor.doctor_name, doctor.doctor_spesialist, doctor.doctor_STR, doctor.doctor_price, doctor.id_jadwal_dokter, doctor.id_riwayat_pendidikan_dokter, doctor.id_riwayat_praktik_dokter)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Integrity error adding doctor")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        conn.close()
    return {"message": "Doctor added successfully"}

@router.get("/getDoctor/{id_doctor}", status_code=status.HTTP_200_OK)
def get_doctor(id_doctor: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Doctor WHERE id_doctor = ?", (id_doctor,))
        doctor = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        conn.close()

    if doctor:
        return {
            "id_doctor": doctor[0],
            "doctor_name": doctor[1],
            "doctor_specialist": doctor[2],
            "doctor_STR": doctor[3],
            "doctor_price": doctor[4],
            "id_jadwal_dokter": doctor[5],
            "id_riwayat_pendidikan_dokter": doctor[6],
            "id_riwayat_praktik_dokter": doctor[7]
        }
    raise HTTPException(status_code=404, detail="Doctor not found")

@router.get("/getDoctorDetails/{id_doctor}", status_code=status.HTTP_200_OK)
def get_doctor_details(id_doctor: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT Doctor.id_doctor, Doctor.doctor_name, Doctor.doctor_spesialist, Doctor.doctor_STR, Doctor.doctor_price,
                      JadwalDokter.hari, JadwalDokter.jam_masuk, JadwalDokter.jam_selesai,
                      RiwayatPendidikan.S1, RiwayatPendidikan.S2, RiwayatPendidikan.S3,
                      RiwayatPraktik.Tempat1, RiwayatPraktik.Tempat2, RiwayatPraktik.Tempat3
               FROM Doctor
               LEFT JOIN JadwalDokter ON Doctor.id_jadwal_dokter = JadwalDokter.id_jadwal_dokter
               LEFT JOIN RiwayatPendidikan ON Doctor.id_riwayat_pendidikan_dokter = RiwayatPendidikan.id_riwayat_pend_dokter
               LEFT JOIN RiwayatPraktik ON Doctor.id_riwayat_praktik_dokter = RiwayatPraktik.id_riwayat_praktik_dokter
               WHERE Doctor.id_doctor = ?""",
            (id_doctor,)
        )
        doctor = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    finally:
        conn.close()

    if doctor:
        return {
            "id_doctor": doctor[0],
            "doctor_name": doctor[1],
            "doctor_specialist": doctor[2],
            "doctor_STR": doctor[3],
            "doctor_price": doctor[4],
            "jadwal": {
                "hari": doctor[5],
                "jam_masuk": doctor[6],
                "jam_selesai": doctor[7],
            },
            "riwayat_pendidikan": {
                "S1": doctor[8],
                "S2": doctor[9],
                "S3": doctor[10],
            },
            "riwayat_praktik": {
                "Tempat1": doctor[11],
                "Tempat2": doctor[12],
                "Tempat3": doctor[13],
            }
        }
    raise HTTPException(status_code=404, detail="Doctor not found")