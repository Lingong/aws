# --------------------------------------------------------------------------------
# 文件：db.py
# 描述：Postgrsql数据库模块
# 版本：0.1
# 作者：lg
# 日期：2020.01.15
# 修改：2020.01.15 0.1 lg  新增版本
# --------------------------------------------------------------------------------

import aiopg
import logging
import psycopg2

from aiopg.transaction import IsolationLevel, Transaction

__all__ = ('Database', 'begin', 'commit', 'rollback')

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(module)s.%(funcName)s[line:%(lineno)d] %(levelname)s:%(message)s',
    datefmt='%Y%m%d %H:%M:%S')

class Database(object):
    pool = None
    conn = None
    cursor = None
    tran = None
    # 占位符
    flag = '%s'

    @classmethod
    async def init_db(cls, app):
        db = app['db']
        if db.dbtype == 'postgresql':
            cls.flag = '%s'
            dsn = 'dbname=%s user=%s password=%s host=%s port=%d' %(
                db.dbname, db.user, db.password, db.host, db.port)
            cls.pool = await aiopg.create_pool(dsn=dsn, minsize=db.minsize, maxsize=db.maxsize)

        else:
            raise ValueError('数据库类型支持：postgresql')
    
    @classmethod
    async def close_db(cls, app):
        db = app['db']
        if db.dbtype == 'postgresql':
            cls.pool.close()
            await cls.pool.wait_closed()
            cls.pool = None
            cls.conn = None
            cls.cursor = None
            cls.tran = None
        else:
            raise ValueError('数据库类型支持：postgresql')

    @classmethod
    async def change(cls, sql=None, args=None):
        if sql is None:
            raise ValueError('sql执行语句为空')
        logging.info('[ %s %s ]' % (sql, args))
        # 未开启事务处理
        if cls.tran is None:
            async with cls.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(sql)
                    return cursor.rowcount
        else:
            if cls.cursor is None:
                raise psycopg2.ProgrammingError('数据库异常,游标为空')
            await cls.cursor.execute(sql)
            return cls.cursor.rowcount

    @classmethod
    async def select(cls, sql=None, args=None, limit=None, offset=None):
        if isinstance(limit, int) and limit < 1:
            raise ValueError('查询条数不能小于1')
        if not isinstance(limit, int) and limit:
            raise ValueError('参数limit类型非法')

        if isinstance(offset, int) and offset < 0:
            raise ValueError('跳过条数不能小于0')
        if not isinstance(offset, int) and offset:
            raise ValueError('参数offset类型非法')

        if offset and limit is None:
            raise ValueError('跳过条数不为空时，查询条数不能为空')

        if limit:
            sql = '%s limit %d' % (sql, limit)
        if offset:
            sql = '%s offset %d' % (sql, offset)
        logging.info('[ %s %s ]' % (sql, args))
        async with cls.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(sql, args)
                rest = await cursor.fetchall()
        return rest

async def begin():
    if Database.tran is None:
        Database.conn = await Database.pool.acquire()
        Database.cursor = await Database.conn.cursor()
        Database.tran = Transaction(Database.cursor, IsolationLevel.read_committed)
        Database.tran = await Database.tran.begin()
    else:
        raise psycopg2.ProgrammingError('有未提交的事务')

async def commit():
    if isinstance(Database.tran, Transaction):
        await Database.tran.commit()
        Database.tran = None
        Database.cursor.close()
        Database.pool.release(Database.conn)
        Database.conn.close()
    else:
        raise psycopg2.ProgrammingError('事务提交异常')

async def rollback():
    if isinstance(Database.tran, Transaction):
        await Database.tran.rollback()
        Database.tran = None
        Database.cursor.close()
        Database.pool.release(Database.conn)
        Database.conn.close()
    else:
        raise psycopg2.ProgrammingError('事务回滚异常')