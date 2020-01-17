import asyncio
from web import db
from web import config
from model import User

# 管理dsn
admin_dsn = {
  'dbname': 'postgres',
  'dbtype': 'postgresql',
  'user': 'lg',
  'password': 'a1s2d3',
  'host': 'localhost',
  'port': 5432,
  'minsize': 1,
  'maxsize': 10
}

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

def get_config(dsn):
  conf = config.getConfig(dsn)
  app = dict()
  app['db'] = conf
  return app

async def setup_db():
  dbconf = get_config(admin_dsn)
  await db.Database.init_db(dbconf)
  sql = 'drop database if exists %s' %user_dsn['dbname']
  await db.Database.change(sql=sql)
  sql = 'create database %s encoding \'utf8\'' %user_dsn['dbname']
  await db.Database.change(sql=sql)
  print('-   创建数据库成功：%s' %user_dsn['dbname'])
  sql = 'grant all privileges on database %s to %s' %(user_dsn['dbname'], user_dsn['user'])
  await db.Database.change(sql=sql)
  await db.Database.close_db(dbconf)

async def create_tables():
  dbconf = get_config(user_dsn)
  tables = [User]
  print('-   创建表成功: ')
  for table in tables:
    print('-               %s' %table)
    await table.create()
  
async def main():
  print('---------------- 安装开始 ---------------')
  print('- 1.数据库初始化...')
  await setup_db()
  print('- 2.创建表...')
  await create_tables()
  # await db.begin()
  # result = await db.Database.change(sql=sql)
  # print(result)
  # time.sleep(10)
  # await db.commit()

if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())