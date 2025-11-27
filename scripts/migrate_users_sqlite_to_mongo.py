# scripts/migrate_users_sqlite_to_mongo.py
import sqlite3
from mongo_models import user as user_model

SQLITE_DB = 'instance/users.db'  # adjust if different
conn = sqlite3.connect(SQLITE_DB)
cur = conn.cursor()
cur.execute("SELECT id, email, password, created_at FROM users")
rows = cur.fetchall()
for r in rows:
    id_, email, pw_hash, created_at = r
    # If password stored hashed compatible with bcrypt, we can migrate as-is.
    try:
        # If pw_hash is plain text — you must re-hash; that would require users to reset
        user_model.users_coll.insert_one({'name':'', 'email': email.lower(), 'password_hash': pw_hash, 'created_at': created_at})
        print("migrated:", email)
    except Exception as e:
        print("skipped", email, "err:", e)
