import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

query = """ INSERT INTO expenses
        (expense_date, category_id, description, amount, payment_method_id, notes)
    VALUES
        (%s, %s, %s, %s, %s, %s);
"""

cursor.execute("""
    SELECT id, name
    FROM categories
    ORDER BY id;
""")

data = (
    '2026-09-27',
    1,
    'Coffee',
    150.00,
    2,
    'Evening coffee'
)

cursor.execute(query, data)
conn.commit()
print("Expense inserted successfully")
cursor.close()
conn.close()


