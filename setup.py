import asyncio
import aiopg
import hashlib
from web import db
from web import config
from model import Account, Usergroup, Mail, Filelist, Filelog

# 用户dsn
user_dsn = {
    'dbname': 'aws',
    'dbtype': 'postgresql',
    'user': 'lg',
    'password': 'a1s2d3',
    'host': 'localhost',
    'port': 5432,
    'minsize': 1,
    'maxsize': 10
}


async def setup_db():
    dsn = 'dbname=postgres user=lg password=a1s2d3 host=localhost port=5432'
    async with aiopg.connect(dsn) as conn:
        async with conn.cursor() as cursor:
            sql = 'drop database if exists %s' % user_dsn['dbname']
            await cursor.execute(sql)
            sql = 'create database %s encoding \'utf8\'' % user_dsn['dbname']
            await cursor.execute(sql)
            print('-   创建数据库成功：%s' % user_dsn['dbname'])
            sql = 'grant all privileges on database %s to %s' % (user_dsn['dbname'], user_dsn['user'])
            await cursor.execute(sql)


async def create_tables():
    await db.init_db(user_dsn)
    await db.begin()
    tables = [Account, Usergroup, Mail, Filelist, Filelog]
    print('-   创建表成功: ')
    for table in tables:
        print('-               %s' % table)
        await table.create()
    await db.commit()
    await db.close_db(user_dsn)


async def init_data():
    await db.init_db(user_dsn)
    await db.begin()
    print('-   初始化表：account')
    password = 'admin-abc123..'
    passwd_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
    account = Account()
    account.uid ='admin'
    account.name = '管理员'
    account.password = passwd_md5
    account.usergroup = 'admin'
    await account.save()
    print('-   初始化表：usergroup')
    usergroup = Usergroup()
    usergroup.gid = 'admin'
    usergroup.role = 'admin'
    usergroup.name = '管理员'
    await usergroup.save()
    usergroup.gid = 'core'
    usergroup.role = 'user'
    usergroup.name = '核心组'
    await usergroup.save()
    usergroup.gid = 'front'
    usergroup.role = 'user'
    usergroup.name = '前置组'
    await usergroup.save()
    usergroup.gid = 'manger'
    usergroup.role = 'user'
    usergroup.name = '管理组'
    await usergroup.save()
    usergroup.gid = 'chanle'
    usergroup.role = 'user'
    usergroup.name = '渠道组'
    await usergroup.save()
    usergroup.gid = 'public'
    usergroup.role = 'user'
    usergroup.name = '公共'
    await usergroup.save()
    await db.commit()
    rows = await Usergroup.read(where='gid=%s', args=['public'])
    print(rows)
    await db.close_db(user_dsn)


async def main():
    print('---------------- 安装开始 ---------------')
    print('- 1.数据库初始化...')
    await setup_db()
    print('- 2.创建表...')
    await create_tables()
    print('- 3.初始化数据...')
    await init_data()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
