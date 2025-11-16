import sqlite3

def criar_banco():
    conn = sqlite3.connect("censo.db")
    cursor = conn.cursor()

    with open("schema.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print("Banco criado usando schema.sql!")

if __name__ == "__main__":
    criar_banco()
