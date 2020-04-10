# -----------------------------------------------------------------------------
# 文件：api.py
# 描述：api 模块
# 版本：0.1
# 作者：lg
# 日期：2019-08-24
# 修改：2019-08-24 0.1 lg  新增版本
#      2019-09-05 0.2 lg  增加ADS加密解密
# -----------------------------------------------------------------------------

import re
import time
from datetime import datetime
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError
from email.mime.text import MIMEText
from Crypto.Cipher import AES
from Crypto import Random
from binascii import b2a_hex, a2b_hex
from model import Filelog
import sqlalchemy as sa

p = re.compile(r'[^@]+@[^@]+\.[^@]+')

def sendMail(content:str, subject:str, sender:str, receiver:str, password:str, ssl:bool=False):
    '''
    使用smtp发送邮件
    :param content: 邮件内容
    :param subject: 邮件标题
    :param sender: 发送邮件地址
    :param receiver: 接收邮件地址
    :param password: 发送邮件帐号密码
    :param ssl: True - 使用ssl协议发送（465端口） False - 不使用ssl协议发送（25端口）
    :return: True - 成功 False - 失败
    '''
    # 检验发送和接收的邮箱地址 xxx@xxx.xxx
    if not p.match(sender) or not p.match(receiver):
        return {'result': False, 'message': '邮箱地址不合法'}
    host = 'smtp.%s' %sender[sender.find('@')+1:]
    message = MIMEText(content, 'plain', 'utf-8')
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = receiver
    if ssl:
        server = SMTP_SSL(host, 465)
    else:
        server = SMTP(host, 25)
    try:
        server.login(sender, password)
    except SMTPAuthenticationError as e:
        return {'result': False, 'message': 'SMTP邮件服务器登录验证失败'}
    server.sendmail(sender, receiver, message.as_string())
    server.quit()
    return {'result': True, 'message': '邮件发送成功'}

def authSMTP(sender:str, password:str, ssl:bool=False):
    # 检验发送和接收的邮箱地址 xxx@xxx.xxx
    if not p.match(sender):
        return {'result': False, 'message': '邮箱地址不合法'}
    host = 'smtp.%s' % sender[sender.find('@') + 1:]
    if ssl:
        server = SMTP_SSL(host, 465)
    else:
        server = SMTP(host, 25)
    try:
        server.login(sender, password)
    except SMTPAuthenticationError as e:
        return {'result': False, 'message': 'SMTP邮件服务器登录验证失败'}
    server.quit()
    return {'result': True, 'message': 'SMTP邮件服务器登录验证成功'}


def encryptADS(seckey, data):
    '''
    使用ADS加密
    :param seckey: 密钥
    :param data: 明文
    :return: 密文
    '''
    if isinstance(seckey, str):
        seckey = seckey.encode('utf-8')
    # 生成长度等于AES块大小的不可重复的密钥向量
    iv = Random.new().read(AES.block_size)
    # 使用seckey和iv初始化AES对象, 使用MODE_CFB模式
    aes = AES.new(seckey, AES.MODE_CFB, iv)
    # 加密的明文长度必须为16的倍数，如果长度不为16的倍数，则需要补足为16的倍数
    # 将iv（密钥向量）加到加密的密文开头，一起传输
    return b2a_hex(iv + aes.encrypt(data.encode())).decode()

def decryptADS(seckey, ciphertext):
    '''
    使用ADS解密
    :param seckey: 密钥
    :param ciphertext: 密文
    :return: 明文
    '''
    data = a2b_hex(ciphertext)
    if isinstance(seckey, str):
        seckey = seckey.encode('utf-8')
    # 解密的话要用key和iv生成新的AES对象
    aes = AES.new(seckey, AES.MODE_CFB, data[:16])
    # 使用新生成的AES对象，将加密的密文解密
    return aes.decrypt(data[16:]).decode()

async def writeLog(app, fileid, option, conn=None):
    '''
    记日志
    :param app: app
    :param fileid: 文件ID: YYYYMMDD0001
    :param option: 操作类型 00-文件上传 01-文件下载 10-文件设置修改 11-文件下载超限 12-文件过期 13-文件设置无效
    :param conn: 数据库连接： None-使用app[conn]
    :return: True-成功 False-失败
    '''
    if conn == None:
        cur_conn = await app['db'].acquire()
    else:
        cur_conn = conn
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    cursor = await cur_conn.execute(Filelog.select().order_by(sa.desc(Filelog.c.seq)))
    row = await cursor.fetchone()
    if row is None:
        seq = 1
    else:
        if row.seq[0:8] == date:
            seq = int(row.seq[8:14]) + 1
        else:
            seq = 1
    cur_seq = '%s%06d' % (date, seq)
    cursor = await cur_conn.execute(Filelog.insert(),
                                    seq=cur_seq,
                                    fileid=fileid,
                                    option=option,
                                    uid= app['uid'],
                                    remote=app['remote'],
                                    url=app['url'],
                                    create_time=datetime.now())
    if cursor.rowcount == 1:
        if conn is None:
            cur_conn.close()
        return True
    else:
        if conn is None:
            cur_conn.close()
        return  False

# if __name__ == '__main__':
#     # content = 'This is a email for awser project test'
#     # subject = 'Awser project test'
#     # sender = 'tczmlg@163.com'
#     # receiver = '283647179@qq.com'
#     # password = 'as400.163'
#     # urls = ['http://localhost:8080/21638c69cbaa12a3bedaa0c2e25f34fd',
#     #         'http://localhost:8080/cdd6cebfb21d92c3e18634be5d808db9']
#     # content = '\n'.join(urls)
#     # print(content)
#     # email = sendMail(content, subject, sender, receiver, password, True)
#     seckey = 'fjnx.seckey.2019'
#     data = 'this is test'
#     print('密钥:%s' %seckey)
#     ciphertext = encryptADS(seckey, data)
#     print('密文:%s' %ciphertext)
#     text = decryptADS(seckey, ciphertext)
#     print('解密:%s' %text)
