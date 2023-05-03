from .db import cur

res = cur.execute("SELECT name FROM sqlite_master")
print(res.fetchone())
