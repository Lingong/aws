# -----------------------------------------------------------------------------------------------
# 文件: router.py
# 描述: 路由器模块
# 版本: 0.1
# 作者: lg
# 日期: 2019-07-31
# 修改: 2019-07-31 0.1 lg  新增版本
# -----------------------------------------------------------------------------------------------

from functools import wraps
# from page import Page
from .handler import Handler


class Router(object):
    def __init__(self):
        self.handlers = []

    # 装饰器 get
    def get(self, path:str, auth:bool=False):
        def decorator(function):
            @wraps(function)
            def wrapper(*args, **kwargs):
                return function(*args, **kwargs)
            wrapper.__method__ = 'get'
            wrapper.__path__ = path
            wrapper.__auth__ = auth
            self.handlers.append(wrapper)
            return wrapper
        return decorator
    
    # 装饰器 post
    def post(self, path:str, auth:bool=False):
        def decorator(function):
            @wraps(function)
            def wrapper(*args, **kwargs):
                return function(*args, **kwargs)
            wrapper.__method__ = 'post'
            wrapper.__path__ = path
            wrapper.__auth__ = auth
            self.handlers.append(wrapper)
            return wrapper
        return decorator

    def json(self, data):
        return {'type': 'json', 'data': data}

    def redirect(self, url):
        return {'type': 'redirect', 'url': url}

    def string(self, string):
        return {'type': 'str', 'string': string}

    def view(self, file):
        return {'type': 'view', 'file': file}

    # def create_page(self, size, index=1, limit=10):
    #     '''
    #     :param limit: 每页的记录条数
    #     :param index: 请求页数
    #     :param size: 总记录数
    #     :return:
    #     '''
    #     page = Page(size, index, limit)
    #     return {
    #         'pageCount':page.count,              # 总页数
    #         'rowTotal':page.size,                # 总记录数
    #         'offset':page.offset,
    #         'currentPage':page.index,            # 当前页数
    #         'pageSize':page.limit                # 每页记录数
    #         }