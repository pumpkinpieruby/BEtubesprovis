from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

router = APIRouter()

class Pendaftaran(BaseModel):
    id_pendaftaran: Optional[int] = None
    user_id: int
    dokter_id: int
    tanggal: str
    jam: str
    hari: Optional[str] = ""
    nama_pasien: Optional[str] = ""
    nama_dokter: Optional[str] = ""
    poli: Optional[str] = ""

class PendaftaranDetail(BaseModel):
    id_pendaftaran: int
    user_id: int
    dokter_id: int
    tanggal: str
    jam: str
    hari: str
    nama_pasien: str
    nama_dokter: str
    poli: str

class BillDetail(BaseModel):
    nama_pasien: str
    nomor_rekam_medis: str
    tanggal_lahir: str
    tanggal_pembayaran: str
    tenggat_pembayaran: str
    tagihan: float
    total_tagihan: float

class PaymentHistory(BaseModel):
    nama_pasien: str
    nomor_rekam_medis: str
    tanggal_lahir: str
    tanggal_pembayaran: str
    bpjs_number: Optional[str] = None
    total_tagihan: float
    status_pembayaran: Optional[str] = None

class BPJSDetail(BaseModel):
    bpjs_number: str
    nama_pasien: str
    nomor_rekam_medis: str
    tanggal_lahir: str
    tanggal_pembayaran: str

@router.post("/addPendaftaran", status_code=status.HTTP_201_CREATED)
def add_pendaftaran(pendaftaran: Pendaftaran):
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
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

@router.get("/getPendaftaran/{id_pendaftaran}", response_model=PendaftaranDetail)
def get_pendaftaran(id_pendaftaran: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id_pendaftaran, p.user_id, p.dokter_id, p.tanggal, p.jam, p.hari, u.user_nama as nama_pasien, d.doctor_name as nama_dokter, d.doctor_poli as poli
        FROM Pendaftaran p
        JOIN User u ON p.user_id = u.user_id
        JOIN Doctor d ON p.dokter_id = d.id_doctor
        WHERE p.id_pendaftaran = ?
    """, (id_pendaftaran,))
    pendaftaran = cursor.fetchone()
    conn.close()
    if pendaftaran:
        return {
            "id_pendaftaran": pendaftaran[0],
            "user_id": pendaftaran[1],
            "dokter_id": pendaftaran[2],
            "tanggal": pendaftaran[3],
            "jam": pendaftaran[4],
            "hari": pendaftaran[5],
            "nama_pasien": pendaftaran[6],
            "nama_dokter": pendaftaran[7],
            "poli": pendaftaran[8]
        }
    raise HTTPException(status_code=404, detail="Pendaftaran not found")

@router.get("/getPendaftaran/{user_id}", response_model=List[Pendaftaran], status_code=status.HTTP_200_OK)
def get_pendaftaran(user_id: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pendaftaran WHERE user_id = ?", (user_id,))
    registrations = cursor.fetchall()
    conn.close()
    if registrations:
        return [
            {
                "user_id": registration[1],
                "dokter_id": registration[2],
                "tanggal": registration[3],
                "jam": registration[4],
                "hari": registration[5],  # Menambahkan atribut hari
            }
            for registration in registrations
        ]
    raise HTTPException(status_code=404, detail="No registrations found")

@router.get("/getAllPendaftaran/{user_id}", response_model=List[Pendaftaran])
def get_all_pendaftaran(user_id: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id_pendaftaran, p.user_id, p.dokter_id, p.tanggal, p.jam, p.hari, u.user_nama as nama_pasien, d.doctor_name as nama_dokter, d.doctor_poli as poli
        FROM Pendaftaran p
        JOIN User u ON p.user_id = u.user_id
        JOIN Doctor d ON p.dokter_id = d.id_doctor
        WHERE p.user_id = ?
    """, (user_id,))
    pendaftaran = cursor.fetchall()
    conn.close()
    if pendaftaran:
        return [
            {
                "id_pendaftaran": p[0],
                "user_id": p[1],
                "dokter_id": p[2],
                "tanggal": p[3],
                "jam": p[4],
                "hari": p[5],
                "nama_pasien": p[6],
                "nama_dokter": p[7],
                "poli": p[8]
            }
            for p in pendaftaran
        ]
    raise HTTPException(status_code=404, detail="No registration history found")

@router.get("/getActivePendaftaran/{user_id}", response_model=Pendaftaran)
def get_active_pendaftaran(user_id: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id_pendaftaran, p.user_id, p.dokter_id, p.tanggal, p.jam, p.hari, u.user_nama as nama_pasien, d.doctor_name as nama_dokter, d.doctor_poli as poli
        FROM Pendaftaran p
        JOIN User u ON p.user_id = u.user_id
        JOIN Doctor d ON p.dokter_id = d.id_doctor
        WHERE p.user_id = ? AND p.tanggal >= date('now')
        LIMIT 1
    """, (user_id,))
    pendaftaran = cursor.fetchone()
    conn.close()
    if pendaftaran:
        return {
            "id_pendaftaran": pendaftaran[0],
            "user_id": pendaftaran[1],
            "dokter_id": pendaftaran[2],
            "tanggal": pendaftaran[3],
            "jam": pendaftaran[4],
            "hari": pendaftaran[5],
            "nama_pasien": pendaftaran[6],
            "nama_dokter": pendaftaran[7],
            "poli": pendaftaran[8]
        }
    raise HTTPException(status_code=404, detail="No active registration found")


@router.get("/getBillDetail/{id_pendaftaran}", response_model=BillDetail)
def get_bill_detail(id_pendaftaran: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_nama, u.user_no_telp, u.user_tanggal_lahir, p.tanggal, p.jam, d.doctor_price
        FROM Pendaftaran p
        JOIN User u ON p.user_id = u.user_id
        JOIN Doctor d ON p.dokter_id = d.id_doctor
        WHERE p.id_pendaftaran = ?
    """, (id_pendaftaran,))
    pendaftaran = cursor.fetchone()
    conn.close()
    if pendaftaran:
        doctor_price = float(pendaftaran[5])
        total_tagihan = doctor_price + (doctor_price * 0.1)
        return {
            "nama_pasien": pendaftaran[0],
            "nomor_rekam_medis": pendaftaran[1],
            "tanggal_lahir": pendaftaran[2],
            "tanggal_pembayaran": pendaftaran[3],
            "tenggat_pembayaran": pendaftaran[3],  # Asumsikan tenggat sama dengan tanggal pembayaran
            "tagihan": doctor_price,
            "total_tagihan": total_tagihan
        }
    raise HTTPException(status_code=404, detail="Bill detail not found")

@router.get("/getPaymentHistory/{user_id}", response_model=List[PaymentHistory])
def get_payment_history(user_id: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_nama, u.user_no_telp, u.user_tanggal_lahir, p.tanggal, u.user_bpjs, d.doctor_price, p.status
        FROM Pendaftaran p
        JOIN User u ON p.user_id = u.user_id
        JOIN Doctor d ON p.dokter_id = d.id_doctor
        WHERE p.user_id = ?
    """, (user_id,))
    riwayat_pembayaran = cursor.fetchall()
    conn.close()
    if riwayat_pembayaran:
        return [
            {
                "nama_pasien": p[0],
                "nomor_rekam_medis": p[1],
                "tanggal_lahir": p[2],
                "tanggal_pembayaran": p[3],
                "bpjs_number": p[4],
                "total_tagihan": float(p[5]) + (float(p[5]) * 0.1),
                "status_pembayaran": p[6]
            }
            for p in riwayat_pembayaran
        ]
    raise HTTPException(status_code=404, detail="No payment history found")

@router.get("/getBPJSDetail/{user_id}", response_model=BPJSDetail)
def get_bpjs_detail(user_id: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_bpjs, u.user_nama, u.user_no_telp, u.user_tanggal_lahir, p.tanggal
        FROM Pendaftaran p
        JOIN User u ON p.user_id = u.user_id
        WHERE p.user_id = ? AND u.user_bpjs IS NOT NULL
        LIMIT 1
    """, (user_id,))
    bpjs_detail = cursor.fetchone()
    conn.close()
    if bpjs_detail:
        return {
            "bpjs_number": bpjs_detail[0],
            "nama_pasien": bpjs_detail[1],
            "nomor_rekam_medis": bpjs_detail[2],
            "tanggal_lahir": bpjs_detail[3],
            "tanggal_pembayaran": bpjs_detail[4]
        }
    raise HTTPException(status_code=404, detail="BPJS detail not found")