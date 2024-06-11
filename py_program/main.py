from fastapi import FastAPI, HTTPException
from app import app
import user  # Import the user module to register routes
import contact  # Import the contact module to register routes
import ceklab  # Import the ceklab module to register routes
import pendaftaran
import obat
import resep_obat
import dokter
import transaksi
import riwayat_pendidikan
import jadwal_dokter
import faq
import riwayat_praktik_dokter
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"FastAPI CareWave": "Berhasil dijalankan!"}

# Include user router
app.include_router(user.router, prefix="/user", tags=["user"])

# Include contact router
app.include_router(contact.router, prefix="/contacts", tags=["contacts"])

# Include ceklab router
app.include_router(ceklab.router, prefix="/ceklab", tags=["ceklab"])

app.include_router(pendaftaran.router, prefix="/pendaftaran", tags=["pendaftaran"])

app.include_router(obat.router, prefix="/obat", tags=["obat"])

app.include_router(resep_obat.router, prefix="/resep_obat", tags=["resep_obat"])

app.include_router(dokter.router, prefix="/dokter", tags=["dokter"])

app.include_router(transaksi.router, prefix="/transaksi", tags=["transaksi"])

app.include_router(riwayat_pendidikan.router, prefix="/riwayat_pendidikan", tags=["riwayat_pendidikan"])

app.include_router(riwayat_praktik_dokter.router, prefix="/riwayat_praktik_dokter", tags=["riwayat_praktik"])

app.include_router(jadwal_dokter.router, prefix="/jadwal_dokter", tags=["jadwal_dokter"])

app.include_router(faq.router, prefix="/faq", tags=["faq"])



