import sqlite3

con = sqlite3.connect("agregation.db")
cur = con.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS agregation (
        id INTEGER PRIMARY KEY,
        value_2d TEXT,
        level INTEGER,
        parent TEXT,
        scanned BOOLEAN,
        agg_time DATETIME
    )"""
)

data_to_insert = [
    ("A001", 1, None, False, None),
    ("A002", 1, None, False, None),
    ("A003", 1, None, False, None),
    ("A004", 1, None, False, None),
    ("A005", 1, None, False, None),
    ("B001", 1, None, False, None),
    ("B002", 1, None, False, None),
    ("B003", 1, None, False, None),
    ("B004", 1, None, False, None),
    ("B005", 1, None, False, None),
    ("M001", 2, None, False, None),
    ("M002", 2, None, False, None),
    ("M003", 2, None, False, None),
    ("C001", 1, None, False, None),
]

cur.executemany(
    "INSERT INTO agregation (value_2d, level, parent, scanned, agg_time) VALUES (?, ?, ?, ?, ?)",
    data_to_insert,
)

for row in cur.execute("SELECT * FROM agregation"):
    print(row)

con.commit()
con.close()
