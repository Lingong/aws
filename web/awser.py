# -----------------------------------------------------------------------------
# 文件：awser.py
# 描述：web服务主文件
# 版本：0.1
# 作者：lg
# 日期：2019-08-06
# 修改：2019-08-06 0.1 lg  新增版本
# -----------------------------------------------------------------------------

import os
from pathlib import Path
from aiohttp import web
from .db import init_pg,close_pg
from .handler import Handler
from .token import Token
from .middleware import middleware_logger
from .config import Config

class Awser(object):
    def __init__(self, host:str='127.0.0.1', port:int=8888):
        self._host = host
        self._port = port
        self._app = web.Application()
        self._app['host'] = host
        self._app['port'] = port
    
    def setup_config(self, config:Config):
        '''加载配置文件'''
        self._app['config'] = config
        print('setup config success')

    def setup_postgres(self, database:str='awser', host:str='localhost',
        port:int=5432, user:str=None, password:str=None, minsize:int=1, maxsize:int=5):
        '''加载postgres数据库'''
        if user is None:
            raise ValueError('数据库用户不能为空')
        if password is None:
            raise ValueError('数据库密码不能为空')
        postgres = {
            'database': database,
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'minsize': minsize,
            'maxsize': maxsize
        }
        self._app['postgres'] = postgres
        self._app.on_startup.append(init_pg)
        self._app.on_cleanup.append(close_pg)
        print('setup databse success')

    def _get_html(self, file:str):
        try:
            html = open(file,'r')
            message = html.read()
            html.close()
            return message
        except FileNotFoundError as e:
            print('文件没有找到：%s'%e)

    def setup_middleware(self, index:str=None, msg404:str=None, msg500:str=None):
        '''
        加载日志中间件
        参数index为路径/默认处理页面
        参数msg404为未找到页面的默认处理html页面文件
        参数msg500为服务器发生异常报错时默认处理html页面文件
        '''
        message = {}
        if index:
            message['index'] = self._get_html(index)
        if msg404:
            message['msg404'] = self._get_html(msg404)
        if msg500:
            message['msg500'] = self._get_html(msg500)
        self._app.middlewares.append(middleware_logger(message))
        print('setup middlewares success')

    def setup_token(self, secret_key:str=None, exp:int=3600):
        '''加载令牌,密钥为空时，将采用默认密钥'''
        if secret_key is None:
            secret_key = 'async.web'
        self._app['token'] = Token(secret_key, exp)
        print('setup token success')
    
    def setup_routes(self, routes):
        '''加载路由'''
        for handler in routes.handlers:
            self._app.router.add_route(handler.__method__, handler.__path__, Handler(handler))
        print('setup static success')
    
    def setup_static(self, prefix='/static', path:str='static'):
        '''加载静态目录'''
        # web启动目录
        root_path = Path(__file__).parent.parent
        # 静态目录
        static_path = root_path / path
        if not os.path.exists(static_path):
            raise ValueError('静态目录%s不存在' %static_path)
        self._app.router.add_static(prefix, static_path)
        print('setup static success')

    def run(self):
        web.run_app(self._app, host=self._host, port=self._port)