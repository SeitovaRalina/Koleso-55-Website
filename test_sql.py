import sqlite3
print(f"Версия SQLite: {sqlite3.sqlite_version}")
conn = sqlite3.connect(':memory:')
print("SQLite в памяти работает отлично!")