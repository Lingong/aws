from web.orm import Model, Varchar, Bigint, Boolean, Integer, Timestamp, Char

class Account(Model):
    __table__ = 'account'
    # 用户ID
    uid = Varchar(primary_key=True, length=20, enable_null=False)
    # 密码 md5密文
    password = Varchar(length=32)
    # 用户组
    usergroup = Varchar(length=20)
    # 名字
    name = Varchar(length=100)

class Mail(Model):
    __table__ = 'mail'
    # 用户ID
    uid = Varchar(primary_key=True, length=20, enable_null=False)
    # 电子邮件
    mail = Varchar(length=50)
    # 邮箱密码密文
    password = Varchar(length=56)
    # 邮件标题
    subject = Varchar(length=100)

class Usergroup(Model):
    __table__ = 'usergroup'
    # 组ID
    gid = Varchar(primary_key=True, length=20, enable_null=False)
    # 角色 user-普通用户 admin-管理员用户
    role = Varchar(length=5)
    # 组名称
    name = Varchar(length=100)

class Filelist(Model):
    __table__ = 'filelist'
    # 文件ID: YYYYMMDD0001
    fileid = Char(primary_key=True, length=12, enable_null=False)
    # 文件md5
    filemd5 = Varchar(length=32)
    # 文件名 255位长度
    filename = Varchar(length=255)
    # 文件大小
    filesize = Bigint()
    # 文件权限 public-公开 user-用户 group-用户组
    fileaut = Varchar(length=20)
    # 是否设置提取码 true-是 false-否
    getcode = Boolean()
    # 下载限制次数
    range = Integer()
    # 当前下载次数
    download = Integer()
    # 有效期
    validity = Timestamp()
    # 状态 00-正常 01-已发送 10-下载超限 11-时间超限 12-设置无效
    status = Char(length=2)

class Filelog(Model):
    __table__ = 'filelog'
    # 流水号 YYYYMMDD000001
    seq = Char(primary_key=True, length=14, enable_null=False)
    # 文件ID: YYYYMMDD0001
    fileid = Varchar(length=12)
    # 操作类型 00-文件上传 01-文件下载 02-发送链接 10-文件设置修改 11-文件下载超限 12-文件时间超限 13-文件设置无效
    option = Varchar(length=2)
    # 用户ID
    uid = Varchar(length=20)
    # 请求IP xxx.xxx.xxx.xxx
    remote = Varchar(length=15)
    # 请求url
    url = Varchar(length=250)
    # 操作时间
    create_time =  Timestamp()