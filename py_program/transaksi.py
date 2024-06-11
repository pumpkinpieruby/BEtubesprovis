from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
import sqlite3

router = APIRouter()

class Transaksi(BaseModel):
    id_pendaftaran: int
    metode_pembayaran: str
    status_pembayaran: str

@router.post("/addTransaksi", status_code=status.HTTP_201_CREATED)
def add_transaksi(transaksi: Transaksi):
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
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

@router.get("/getTransaksi/{id_pendaftaran}", response_model=List[Transaksi], status_code=status.HTTP_200_OK)
def get_transaksi(id_pendaftaran: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transaksi WHERE id_pendaftaran = ?", (id_pendaftaran,))
    transactions = cursor.fetchall()
    conn.close()
    if transactions:
        return [
            {
                "id_pendaftaran": transaction[1],
                "metode_pembayaran": transaction[2],
                "status_pembayaran": transaction[3]
            }
            for transaction in transactions
        ]
    raise HTTPException(status_code=404, detail="No transactions found")
