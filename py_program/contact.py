from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
import sqlite3

router = APIRouter()

# Pydantic model for urgent contact data
class UrgentContact(BaseModel):
    user_id: int
    urgent_contact_name: str
    urgent_contact_desc: str
    urgent_contact_notelp: str

# Init db for urgent contacts
@router.get("/init/", status_code=status.HTTP_201_CREATED)
def init_db():
    try:
        conn = sqlite3.connect("carewave.db")
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Urgent_Contact(
                urgent_contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                urgent_contact_name TEXT NOT NULL,
                urgent_contact_desc TEXT NOT NULL,
                urgent_contact_notelp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES user (user_id))"""
        )
        conn.commit()
    except Exception as e:
        return {"status": f"Error saat membuat tabel: {e}"}
    finally:
        conn.close()
    return {"status": "Berhasil membuat tabel Urgent_Contact"}

# Adding urgent contact
@router.post("/addUrgentContact", status_code=status.HTTP_201_CREATED)
def add_urgent_contact(urgent_contact: UrgentContact):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO Urgent_Contact (user_id, urgent_contact_name, urgent_contact_desc, urgent_contact_notelp)
            VALUES (?, ?, ?, ?)""",
            (urgent_contact.user_id, urgent_contact.urgent_contact_name, urgent_contact.urgent_contact_desc, urgent_contact.urgent_contact_notelp)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Error adding urgent contact")
    finally:
        conn.close()
    return {"message": "Urgent contact added successfully"}

# Getting all urgent contacts for a user
@router.get("/getUrgentContacts/{user_id}", status_code=status.HTTP_200_OK)
def get_urgent_contacts(user_id: int):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Urgent_Contact WHERE user_id = ?", (user_id,))
    contacts = cursor.fetchall()
    conn.close()
    if contacts:
        return [
            {
                "urgent_contact_id": contact[0],
                "user_id": contact[1],
                "urgent_contact_name": contact[2],
                "urgent_contact_desc": contact[3],
                "urgent_contact_notelp": contact[4],
            }
            for contact in contacts
        ]
    raise HTTPException(status_code=404, detail="No urgent contacts found")
