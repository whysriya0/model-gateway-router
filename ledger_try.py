import sqlite3
from app import ledger

ledger.init_db()
cost=ledger.log_request('test1','openai/gpt-oss-20b', 77,113,650.0,'ok')
print("cost:",cost)
cost=ledger.log_request('test2', 'openai/gpt-oss-120b', 60, 150, 650.0, 'ok')
rows=sqlite3.connect('ledger.db').execute('select * from requests').fetchall()
for r in rows:
    print(r)
