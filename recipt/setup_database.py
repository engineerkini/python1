import sqlite3

def setup_database():
    conn = sqlite3.connect('kra_returns.db')
    cursor = conn.cursor()

    # Create table for transactions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        vat REAL NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()