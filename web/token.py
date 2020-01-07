# ----------------------------------------------------------------------------------------------------------
# 文件: token.py
# 描述: token模块
# 版本: 0.1
# 作者: lg
# 日期: 2019-07-31
# 修改: 2019-07-31 0.1 lg  新增版本
# ----------------------------------------------------------------------------------------------------------

import jwt
import time
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(module)s.%(funcName)s[line:%(lineno)d] %(levelname)s:%(message)s',
                    datefmt='%Y%m%d %H:%M:%S')

class Token(object):
  def __init__(self, key:str, exp:int):
    self._secret_key = key
    self._exp = exp

  def setToken(self, key:str, exp:int):
    self._secret_key = key
    self._exp = exp

  def genToken(self, uid:str):
    payload = {
      'iss': 'fjnx.mark',
      'iat': int(time.time()),
      'exp': int(time.time()) + self._exp,
      'uid': uid
    }
    token = jwt.encode(payload,self._secret_key,algorithm='HS256')
    logging.info('token = [%s]'%token)
    return token.decode()

  def verifyToken(self,token:str):
    try:
      payload = jwt.decode(token,self._secret_key,algorithms=['HS256'])
    except Exception as e:
      logging.info('Error:%s'%e)
      return None
    if payload:
      logging.info('verify token success')
      return payload['uid']
    else:
      logging.info('verify token fail')
      return None