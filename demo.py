import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()
cursor.execute('create table demo(id varchar(10) primary key, name varchar(100))')
cursor.execute('insert into demo(id, name) values(\'1\', \'lingong\')')
cursor.execute('select * from demo')
rows = cursor.fetchall()
for line in rows:
  print(line)
cursor.close()
conn.close()