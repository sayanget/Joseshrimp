import sqlite3

conn = sqlite3.connect('instance/sales.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f'Tables found: {len(tables)}')
for t in tables:
    print(f'  - {t[0]}')
conn.close()
