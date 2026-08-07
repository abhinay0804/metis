import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('/mnt/shared/Projects/Metis/metis.db')
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE users ADD COLUMN photo_base64 TEXT;")
        conn.commit()
        print("Migration successful: Added photo_base64 to users table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column already exists.")
        else:
            print("Error:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
