# -----------------------------------------------------------------------------
# 文件：config.py
# 描述：配置文件
# 版本：0.2
# 作者：lg
# 日期：2019.08.02
# 修改：2019.08.02 0.1 lg  新增版本
#      2020.01.15 0.2 lg  修改getConfig函数，新增loadConfig函数，删除dict_to_obj函数
# -----------------------------------------------------------------------------

from yaml import safe_load

class Config(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__

def getConfig(dictObj: dict):
    if not isinstance(dictObj, dict):
        return dictObj
    inst = Config()
    for k,v in dictObj.items():
        inst[k] = getConfig(v)
    return inst

def loadConfig(file:str):
    with open(file, 'r') as conf:
        config = safe_load(conf.read())
        return getConfig(config)
