from web.config import getConfig
from web.awser import Awser
from views import routes

if __name__ == '__main__':
    # 导入配置
    config = getConfig('config.yaml')
    app = Awser()
    # 导入配置文件
    app.setup_config(config)
    # 导入数据库
    app.setup_postgres(user=config.postgres.user, password=config.postgres.password)
    # 导入中间件
    app.setup_middleware(index='index.html', msg404='index.html')
    # 导入令牌
    app.setup_token(secret_key=config.token.secret_key)
    # 导入静态目录
    app.setup_static(path=config.web.static)
    # 导入路由
    app.setup_routes(routes)
    # 运行
    app.run()