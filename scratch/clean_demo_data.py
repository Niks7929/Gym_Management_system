import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', database='setfit_gym')
cur = conn.cursor()

# 1. Remove demo user yyy@gmail.com and related records
cur.execute("SELECT id FROM users WHERE email = 'yyy@gmail.com';")
user_row = cur.fetchone()
if user_row:
    user_id = user_row[0]
    print(f"Found demo user yyy@gmail.com with ID: {user_id}")
    cur.execute("SELECT id FROM members WHERE user_id = %s;", (user_id,))
    mem_row = cur.fetchone()
    if mem_row:
        mem_id = mem_row[0]
        cur.execute("DELETE FROM payments WHERE member_id = %s;", (mem_id,))
        cur.execute("DELETE FROM memberships WHERE member_id = %s;", (mem_id,))
        cur.execute("DELETE FROM attendance WHERE member_id = %s;", (mem_id,))
        cur.execute("DELETE FROM trainer_members WHERE member_id = %s;", (mem_id,))
        cur.execute("DELETE FROM workout_plans WHERE member_id = %s;", (mem_id,))
        cur.execute("DELETE FROM diet_plans WHERE member_id = %s;", (mem_id,))
        cur.execute("DELETE FROM members WHERE id = %s;", (mem_id,))
    cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))
    print("Deleted demo user yyy@gmail.com and all associated records.")

# 2. Delete test/demo enquiries
cur.execute("DELETE FROM enquiries WHERE email LIKE '%@example.com' OR email LIKE '%@test.com' OR name LIKE '%Test%' OR name = 'Rohan Deshmukh';")
print(f"Deleted {cur.rowcount} test/demo enquiries.")

# 3. Update demo names to proper clean names
cur.execute("UPDATE users SET first_name='Gym', last_name='Admin' WHERE email='admin@setfitgym.com';")
cur.execute("UPDATE users SET first_name='Rutuja', last_name='Shinde' WHERE email='rutuja@gmail.com';")
cur.execute("UPDATE users SET first_name='Gayatri', last_name='Patil' WHERE email='gayatri@gmail.com';")

conn.commit()

# Verify
cur.execute("SELECT id, email, first_name, last_name, role FROM users;")
print("Users in DB:", cur.fetchall())
cur.execute("SELECT id, name, email FROM enquiries;")
print("Enquiries in DB:", cur.fetchall())

conn.close()
print("Demo cleanup completed successfully!")
