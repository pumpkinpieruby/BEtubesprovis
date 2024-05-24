from fastapi import FastAPI, HTTPException
from app import app
import user  # Import the user module to register routes
import contact  # Import the contact module to register routes
import ceklab  # Import the ceklab module to register routes

@app.get("/")
def read_root():
    return {"FastAPI CareWave": "Berhasil dijalankan!"}

# Include user router
app.include_router(user.router)

# Include contact router
app.include_router(contact.router, prefix="/contacts", tags=["contacts"])

# Include ceklab router
app.include_router(ceklab.router, prefix="/ceklab", tags=["ceklab"])
