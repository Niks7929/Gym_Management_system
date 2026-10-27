import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', database='setfit_gym')
cur = conn.cursor()

# 1. Truncate/Clear all transactional tables
tables_to_clear = [
    'attendance',
    'workout_exercises',
    'workout_plans',
    'diet_meals',
    'diet_plans',
    'trainer_members',
    'payments',
    'memberships',
    'members',
    'trainers',
    'enquiries',
    'audit_logs'
]

cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
for tbl in tables_to_clear:
    cur.execute(f"DELETE FROM {tbl};")
    print(f"Cleared table: {tbl}")

# 2. Delete non-admin users
cur.execute("DELETE FROM users WHERE role != 'admin';")
print("Deleted all non-admin users.")

# 3. Update Admin user to clean official credentials
cur.execute("UPDATE users SET first_name='Admin', last_name='' WHERE role='admin';")
print("Updated admin name to 'Admin'.")

cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()

# 4. Verify
cur.execute("SELECT id, email, first_name, last_name, role FROM users;")
print("Remaining users:", cur.fetchall())
for tbl in tables_to_clear:
    cur.execute(f"SELECT COUNT(*) FROM {tbl};")
    print(f"{tbl} count:", cur.fetchone()[0])

conn.close()
print("All demo data and demo names completely cleared from database!")
