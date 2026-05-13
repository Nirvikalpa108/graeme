from utils import db_connection

with open("init.sql") as f:
    sql = f.read()

with db_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute(sql)
    conn.commit()

print("✅ Database schema initialised")
