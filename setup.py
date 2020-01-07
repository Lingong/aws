import hashlib
import os
from sqlalchemy import create_engine,MetaData
from model import User, Group, Filelist, Mail, Filelog
from web.config import getConfig

config = getConfig('config.yaml')
pg = config.postgres

dsn = 'postgresql://{user}:{password}@{host}:{port}/{database}'
admin_dsn = dsn.format(user='postgres', password='a1s2d3', database='postgres', host='localhost', port=5432)
user_dsn = dsn.format(user=pg.user, password=pg.password, host=pg.host, port=pg.port, database=pg.database)

admin_engine = create_engine(admin_dsn, isolation_level='AUTOCOMMIT')
user_engine = create_engine(user_dsn, isolation_level='AUTOCOMMIT')

tables = [User, Group, Filelist, Mail, Filelog]

def setup_db():
    conn = admin_engine.connect()
    conn.execute('drop database if exists %s' %pg.database)
    conn.execute('drop role if exists %s' %pg.user)
    conn.execute('create user %s with password \'%s\'' %(pg.user,pg.password))
    print('-   创建用户成功：%s' %pg.user)
    conn.execute('create database %s encoding \'utf8\'' %pg.database)
    print('-   创建数据库成功：%s' %pg.database)
    conn.execute('grant all privileges on database %s to %s' %(pg.database,pg.user))
    conn.close()

def create_tables(engine=user_engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=tables)
    print('-   创建表成功: ')
    for table in tables:
        print('-               %s' %table)

def drop_tables(engine=user_engine):
    meta = MetaData()
    meta.drop_all(bind=engine, tables=tables)
    print('-   删除表成功:')
    print(tables)

def init_data(engine=user_engine):
    conn = engine.connect()
    password = 'admin-abc123..'
    passwd_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
    conn.execute(User.insert().values(uid='admin',password=passwd_md5,group='admin',name='管理员'))
    print('-   初始化表：User')
    conn.execute(Group.insert().values(gid='admin',role='admin',name='管理员'))
    conn.execute(Group.insert().values(gid='core',role='user',name='核心组'))
    conn.execute(Group.insert().values(gid='front',role='user',name='前置组'))
    conn.execute(Group.insert().values(gid='manger',role='user',name='管理组'))
    conn.execute(Group.insert().values(gid='chanle',role='user',name='渠道组'))
    conn.execute(Group.insert().values(gid='public',role='user',name='公共'))
    print('-   初始化表：Group')
    conn.close()

def init_dir():
    if not os.path.exists(config.web.path):
        os.mkdir(config.web.path)
    print('-   初始化目录：%s'%config.web.path)
    if not os.path.exists(config.web.static):
        os.mkdir(config.web.static)
    print('-   初始化目录：%s'%config.web.static)

if __name__ == '__main__':
    print('---------------- 安装开始 ---------------')
    print('- 1.数据库初始化...')
    setup_db()
    print('- 2.创建表...')
    create_tables()
    print('- 3.初始化数据...')
    init_data()
    print('- 4.初始化目录')
    init_dir()
    print('---------------- 安装完成 ---------------')
