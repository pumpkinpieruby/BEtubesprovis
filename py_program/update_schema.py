import sqlite3

def update_schema():
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()

    # Menambahkan kolom 'status' jika belum ada
    cursor.execute("PRAGMA table_info(Pendaftaran);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'status' not in columns:
        cursor.execute("ALTER TABLE Pendaftaran ADD COLUMN status TEXT DEFAULT NULL;")

    # Commit perubahan dan tutup koneksi
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_schema()
