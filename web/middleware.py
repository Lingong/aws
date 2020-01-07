# -----------------------------------------------------------------------------
# 文件：middleware.py
# 描述：中间件
# 版本：0.2
# 作者：lg
# 日期：2019-07-31
# 修改：2019-07-31 0.1 lg  新增版本
#      2019-08-17 0.2 lg  增加返回404和500以及默认路径/的处理页面
# -----------------------------------------------------------------------------
import logging
from aiohttp import web

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(module)s.%(funcName)s[line:%(lineno)d] %(levelname)s:%(message)s',
    datefmt='%Y%m%d %H:%M:%S')

def middleware_logger(message:dict):
    '''
    参数message为dict:
    index ：为当访问路径为/并且没有定义路由时的处理信息
    msg404：为当找不到路径（404）的默认处理信息
    msg505：为当服务器发生异常（500）的默认处理信息       
    '''
    @web.middleware
    async def logger(request, handler):
        try:
            logging.info('%s [request:%s %s %s]' 
            %(request.host, request.method, request.path, request.content_type))
            index = message.get('index')
            if index and request.path == '/':
                return web.Response(text=index, content_type='text/html')
            response = await handler(request)
            status = response.status
            if status not in (404, 500):
                logging.info('[response success status: %s]' %status)
                return response
            msg = response.message
        except web.HTTPException as ex:
            status = ex.status
            if status not in (404, 500):
                raise
            msg = ex.reason
        logging.info('[response error(%s): %s]' %(status, msg))
        msg404 = message.get('msg404')
        if msg404:
            return web.Response(text=msg404, content_type='text/html')
        msg500 = message.get('msg500')
        if msg500:
            return web.Response(text=msg500, content_type='text/html')
        return web.Response(text='response error(%s): %s' %(status, msg))
    return logger