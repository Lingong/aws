# -----------------------------------------------------------------------------
# 文件：handler.py
# 描述：该文件主要是对request封装
# 版本：0.2
# 作者：lg
# 日期：2018-03-22
# 修改：2018-03-22 0.1 lg  新增版本
#      2019-07-31 0.2 lg  修改request入口参数
# -----------------------------------------------------------------------------
import logging
import inspect
from urllib import parse
from aiohttp import web

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(module)s.%(funcName)s[line:%(lineno)d] %(levelname)s:%(message)s',
    datefmt='%Y%m%d %H:%M:%S')

class Handler(object):
    def __init__(self, func):
        self._func = func
        
    async def __call__(self, request):
        kw = None
        uid = None
        logging.info('[Handler %s %s %s]'% (request.method, request.path, request.content_type))
        # 授权路径token检查
        if self._func.__auth__:
            token = request.headers.get('Authorization')
            logging.info('[Handler token: %s ]' %token)
            # token 为空
            if token is None:
                data = {'result': False, 'message':'token is none'}
                return web.json_response(data=data, status=401)
            # token 检验
            uid = request.app['token'].verifyToken(token)
            if uid is None:
                data = {'result': False, 'message':'invalid token'}
                return web.json_response(data=data, status=401)
        # 解析get请求
        if request.method == 'GET':
            qs = request.query_string
            if qs:
                logging.info('[Handler query_string: %s ]' % qs)
                kw = dict()
                for k, v in parse.parse_qs(qs, True).items():
                    kw[k] = v[0]
        # 解析post请求
        if request.method == 'POST':
            if not request.content_type:
                return web.HTTPBadRequest('Missing Content-Type.')
            ct = request.content_type.lower()
            if ct.startswith('application/json'):
                data = await request.json()
                if not isinstance(data, dict):
                    return web.HTTPBadRequest('JSON body must be object.')
                kw = data
            elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                data = await request.post()
                kw = dict(**data)
            else:
                return web.HTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)

        if kw is None:
            kw = dict(**request.match_info)
        # 参数解析
        params = inspect.signature(self._func).parameters
        for param in params:
            if param == 'app':
                request.app['uid'] = uid
                request.app['remote'] = request.remote
                request.app['url'] = str(request.url)
                kw['app'] = request.app
        logging.info('[Handler keyword = %s]' % kw)
        response = await self._func(**kw)
        return response