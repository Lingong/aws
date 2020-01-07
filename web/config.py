# -----------------------------------------------------------------------------
# 文件：config.py
# 描述：配置文件
# 版本：0.1
# 作者：lg
# 日期：2019-08-02
# 修改：2019-08-02 0.1 lg  新增版本
# -----------------------------------------------------------------------------

from yaml import safe_load

class Config(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__

def dict_to_object(dictObj):
    if not isinstance(dictObj, dict):
        return dictObj
    inst = Config()
    for k,v in dictObj.items():
        inst[k] = dict_to_object(v)
    return inst

def getConfig(file:str):
    with open(file, 'r') as conf:
        config = safe_load(conf.read())
        return dict_to_object(config)

# if __name__ == '__main__':
#     config = get_config('../config.yaml')
#     print(config)
#     web = config.web
#     print(web.host)