import aiopg
import asyncio
from aiopg.transaction import IsolationLevel, Transaction

async def db():
    dsn = 'dbname=aws user=lg password=a1s2d3 host=localhost port=5432'
    pool = await aiopg.create_pool(dsn=dsn, minsize=1, maxsize=10)
    conn = await pool.acquire()
    cursor = await conn.cursor()
    # tran = Transaction(cursor, IsolationLevel.read_committed)
    # tran = await tran.begin()
    await cursor.execute('create table test(uid varchar(10),primary key(uid))')
    # await tran.commit()
    cursor.close()
    pool.release(conn)
    conn.close()
    pool.close()
    await pool.wait_closed()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(db())