from datetime import datetime

from web.orm import Model, Varchar

class User(Model):
    __table__ = 'user'
    # 用户ID
    uid = Varchar(primary_key=True, length=20)
    # 密码 md5密文
    password = Varchar(length=32)
    # 用户组
    group = Varchar(length=20)
    # 名字
    name = Varchar(length=100)

# Mail = Table(
#     'mail', meta,
#     # 用户ID
#     Column('uid', String(20), primary_key=True),
#     # 电子邮件
#     Column('mail', String(50), nullable=False),
#     # 邮箱密码密文
#     Column('password', String(56)),
#     # 邮件标题
#     Column('subject', String(100))
# )

# Group = Table(
#     'group', meta,
#     # 组ID
#     Column('gid', String(20), primary_key=True),
#     # 角色 user-普通用户 admin-管理员用户
#     Column('role', String(5)),
#     # 组名称
#     Column('name', String(100))
# )

# Filelist = Table(
#     'filelist', meta,
#     # 文件ID: YYYYMMDD0001
#     Column('fileid', String(12), primary_key=True),
#     # 文件md5
#     Column('filemd5', String(32)),
#     # 文件名 255位长度
#     Column('filename', String(255)),
#     # 文件大小
#     Column('filesize', BIGINT),
#     # 文件权限 public-公开 user-用户 group-用户组
#     Column('fileaut', String(20)),
#     # 是否设置提取码 true-是 false-否
#     Column('getcode', Boolean),
#     # 下载限制次数
#     Column('limit', Integer),
#     # 当前下载次数 
#     Column('download', Integer),
#     # 有效期
#     Column('validity', Date),
#     # 状态 00-正常 01-已发送 10-下载超限 11-时间超限 12-设置无效
#     Column('status', String(2))
# )

# Filelog = Table(
#     'filelog', meta,
#     # 流水号 YYYYMMDD000001
#     Column('seq', String(14), primary_key=True),
#     # 文件ID: YYYYMMDD0001
#     Column('fileid', String(12)),
#     # 操作类型 00-文件上传 01-文件下载 02-发送链接 10-文件设置修改 11-文件下载超限 12-文件时间超限 13-文件设置无效
#     Column('option', String(2)),
#     # 用户ID
#     Column('uid', String(20)),
#     # 请求IP xxx.xxx.xxx.xxx
#     Column('remote', String(15)),
#     # 请求url
#     Column('url', String(250)),
#     # 操作时间
#     Column('create_time', DateTime)
# )