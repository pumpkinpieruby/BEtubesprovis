from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
import sqlite3

router = APIRouter()

# Pydantic model for transaction data
class Transaksi(BaseModel):
    id_pendaftaran: int
    metode_pembayaran: str
    status_pembayaran: str

# Init db for transaksi
@router.get("/init_transaksi/", status_code=status.HTTP_201_CREATED)
def init_db_transaksi():
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS transaksi (
                id_transaksi INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pendaftaran INTEGER NOT NULL,
                metode_pembayaran TEXT NOT NULL,
                status_pembayaran TEXT NOT NULL,
                FOREIGN KEY (id_pendaftaran) REFERENCES pendaftaran (id_pendaftaran)
            )"""
        )
        conn.commit()
    except Exception as e:
        return {"status": f"Error saat membuat tabel: {e}"}
    finally:
        conn.close()
    return {"status": "Berhasil membuat tabel transaksi"}

# Adding transaction
@router.post("/addTransaksi", status_code=status.HTTP_201_CREATED)
def add_transaksi(transaksi: Transaksi):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO transaksi (id_pendaftaran, metode_pembayaran, status_pembayaran)
            VALUES (?, ?, ?)""",
            (transaksi.id_pendaftaran, transaksi.metode_pembayaran, transaksi.status_pembayaran)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Error adding transaction")
    finally:
        conn.close()
    return {"message": "Transaction added successfully"}

# Getting all transactions for a registration
@router.get("/getTransaksi/{id_pendaftaran}", status_code=status.HTTP_200_OK)
def get_transaksi(id_pendaftaran: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transaksi WHERE id_pendaftaran = ?", (id_pendaftaran,))
    transactions = cursor.fetchall()
    conn.close()
    if transactions:
        return [
            {
                "id_transaksi": transaction[0],
                "id_pendaftaran": transaction[1],
                "metode_pembayaran": transaction[2],
                "status_pembayaran": transaction[3],
            }
            for transaction in transactions
        ]
    raise HTTPException(status_code=404, detail="No transactions found")
