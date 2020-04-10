import os
import time
import hashlib
import api
import datetime
import sqlalchemy as sa
from aiohttp import web
from model import User, Group, Filelist, Mail, Filelog
from web.router import Router
from web.page import getPage

routes = Router()


@routes.post('/app/auth')
async def login(app, uid, password):
    async with app['db'].acquire() as conn:
        cuser = await conn.execute(User.select().where(User.c.uid == uid))
        ruser = await cuser.fetchone()
        if ruser is None:
            return web.json_response({'result': False, 'message': '用户%s不存在' %uid})
        if ruser.password != password:
            return web.json_response({'result': False, 'message': '密码错误'})
        cgroup = await conn.execute(Group.select().where(Group.c.gid == ruser.group))
        rgroup = await cgroup.fetchone()
        if rgroup is None:
            return web.json_response({'result': False, 'message': '用户组%s不存在' %ruser.group})
        token = app['token'].genToken(uid)
        data = {'result': True, 'role': rgroup.role, 'token': token, 'message': 'login success'}
        return web.json_response(data)


@routes.post('/root/password', True)
async def password(app, uid, oldpwd, newpwd):
    async with app['db'].acquire() as conn:
        cursor = await conn.execute(User.select().where(User.c.uid == uid))
        row = await cursor.fetchone()
        if row:
            if row.password != oldpwd:
                return web.json_response({'result': False, 'message': '用户%s的原密码错误' % uid})
        else:
            return web.json_response({'result': False, 'message': '用户%s不存在' % uid})
        cursor = await conn.execute(User.update().where(User.c.uid == uid).values(password=newpwd))
        if cursor.rowcount == 1:
            return web.json_response({'result': True, 'message': '用户%s密码修改成功' % uid})
        else:
            return web.json_response({'result': False, 'message': '用户%s密码修改失败' % uid})


@routes.post('/root/reset', True)
async def reset(app, uid):
    async with app['db'].acquire() as conn:
        join = sa.join(User, Group, User.c.group == Group.c.gid)
        query = (sa.select([User.c.uid, Group.c.role])
                 .select_from(join).where(User.c.uid == app['uid']))
        cursor = await conn.execute(query)
        row = await cursor.fetchone()
        if row is None:
            return web.json_response({'result': False, 'message': '用户%s密码重置失败' % uid})
        if row.role != 'admin':
            return web.json_response({'result': False, 'message': '非管理员用户不能重置密码'})
        password = '%s-abc123..' % uid
        passwd_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
        cursor = await conn.execute(User.update().where(User.c.uid == uid).values(password=passwd_md5))
        if cursor.rowcount == 1:
            return web.json_response({'result': True, 'message': '密码重置成功,新密码[abc123..]' })
        else:
            return web.json_response({'result': True, 'message': '用户%s密码重置数据库更新失败' % uid})


@routes.get('/root/groups', True)
async def groups(app):
    async with app['db'].acquire() as conn:
        cursor = await conn.execute(Group.select().where(Group.c.role == 'user'))
        row = await cursor.fetchall()
        data = []
        if row:
            data = [dict(g) for g in row]
        return web.json_response(data=data)


@routes.get('/root/users', True)
async def users(app):
    async with app['db'].acquire() as conn:
        join = sa.join(User, Group, User.c.group == Group.c.gid)
        query = (sa.select([User.c.uid, User.c.name, Group.c.name.label('gname')])
                 .select_from(join).where(User.c.uid != app['uid']))
        cursor = await conn.execute(query)
        rows = await cursor.fetchall()
        data = []
        if rows:
            data = [dict(g) for g in rows]
        return web.json_response(data=data)


@routes.post('/root/remove/group', True)
async def removeGroup(app, gid):
    async with app['db'].acquire() as conn:
        cursor = await conn.execute(User.select().where(User.c.group == gid))
        row = await cursor.fetchone()
        if row:
            return web.json_response({'result': False, 'message': '组%s下存在用户' % gid})
        cursor = await conn.execute(Group.delete().where(Group.c.gid == gid))
        if cursor.rowcount == 1:
            return web.json_response({'result': True, 'message': '删除组%s成功' % gid})
        else:
            return web.json_response({'result': False, 'message': '删除组%s失败' % gid})


@routes.post('/root/remove/user', True)
async def removeUser(app, uid):
    async with app['db'].acquire() as conn:
        cursor = await conn.execute(User.delete().where(User.c.uid == uid))
        if cursor.rowcount == 1:
            return web.json_response({'result': True, 'message': '删除用户%s成功' % uid})
        else:
            return web.json_response({'result': False, 'message': '删除用户%s失败' % uid})


@routes.post('/root/add', True)
async def add(app, gid, name):
    async with app['db'].acquire() as conn:
        cursor = await conn.execute(Group.select().where(Group.c.gid == gid))
        row = await cursor.fetchone()
        if row:
            return web.json_response({'result': False, 'message': '组%s已存在' % gid})
        else:
            cursor = await conn.execute(Group.insert().values(gid = gid, name = name, role = 'user'))
            if cursor.rowcount == 1:
                return web.json_response({'result': True, 'message': '新增组%s成功' % gid})
            else:
                return web.json_response({'result': False, 'message': '新增组%s失败' % gid})


@routes.get('/app/auts', True)
async def auts(app):
    async with app['db'].acquire() as conn:
        cgroup = await conn.execute(Group.select().where(Group.c.role == 'user'))
        rgroup = await cgroup.fetchall()
        data = []
        if rgroup:
            for group in rgroup:
                data.append({'autid': group.gid, 'name': group.name})
        join = sa.join(User, Group, User.c.group == Group.c.gid)
        query = (sa.select([User.c.uid, User.c.name])
                 .select_from(join).where(Group.c.role != 'admin'))
        cuser = await conn.execute(query)
        ruser = await cuser.fetchall()
        if ruser:
            for user in ruser:
                data.append({'autid': user.uid, 'name': user.name})
        return web.json_response(data=data)


@routes.post('/root/register')
async def register(app, uid, password, name, group):
    async with app['db'].acquire() as conn:
        # 检查用户是否存在
        cuser = await conn.execute(User.select().where(User.c.uid == uid))
        ruser = await cuser.fetchone()
        if ruser:
            return web.json_response({'result': False, 'message': '用户%s已存在' % uid})
        else:
            # 检查用户组是否存在
            cgroup = await conn.execute(Group.select().where(Group.c.gid == group))
            rgroup = await cgroup.fetchone()
            if rgroup is None:
                return web.json_response({'result': False, 'message': '用户组%s不存在' % group})
            await conn.execute(User.insert(), uid=uid, password=password, group=group, name=name)
            return web.json_response({'result': True, 'message': '用户%s(%s)注册成功' % (uid, name)})


@routes.post('/app/filelist', True)
async def filelist(app, status, index, limit):
    async with app['db'].acquire() as conn:
        # 检查用户是否存在
        cuser = await conn.execute(User.select().where(User.c.uid == app['uid']))
        ruser = await cuser.fetchone()
        if ruser is None:
            return web.json_response({'result': False, 'message': '用户不存在'})
        # 查询文件清单
        query = (sa.select([sa.func.count(Filelist.c.fileid)]).select_from(Filelist)
                .where(sa.and_(Filelist.c.fileaut.in_((app['uid'], 'public', ruser.group)),
                    Filelist.c.status.in_(status))))
        cursor = await conn.execute(query)
        count = await cursor.fetchone()
        page = getPage(count[0], index, limit)
        query = (sa.select([Filelist]).limit(page['limit']).offset(page['offset']).select_from(Filelist)
                .where(sa.and_(Filelist.c.fileaut.in_((app['uid'], 'public', ruser.group)),
                    Filelist.c.status.in_(status)))
                .order_by(sa.desc(Filelist.c.fileid)))
        cursor = await conn.execute(query)
        rows = await cursor.fetchall()
        data = []
        if rows:
            for row in rows:
                row = dict(row)
                row['validity'] = row['validity'].strftime('%Y-%m-%d')
                data.append(row)
        else:
            data = []
        return web.json_response({ 'result': True, 'rows': data, 'page': page })


@routes.post('/app/upload', True)
async def upload(app, file):
    # 生成文件ID
    date = time.strftime('%Y%m%d', time.localtime(time.time()))
    full_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    async with app['db'].acquire() as conn:
        cfile = await conn.execute(Filelist.select().order_by(sa.desc(Filelist.c.fileid)))
        rfile = await cfile.fetchone()
        if rfile is None:
            seq = 1
        else:
            if rfile.fileid[0:8] == date:
                seq = int(rfile.fileid[8:12]) + 1
            else:
                seq = 1
        fileid = '%s%04d' % (date, seq)
        filename = os.path.join(app['config'].web.path, fileid)
        rfile = file.file
        wfile = open(filename, 'wb')
        byte_data = rfile.read()
        wfile.write(byte_data)
        wfile.close()
        size = os.path.getsize(filename)
        result = await conn.execute(Filelist.insert(),
            fileid=fileid,
            filemd5=None,
            filename=file.filename,
            filesize=size,
            fileaut=app['uid'],
            getcode=True,
            limit=5,
            download=0,
            validity=full_date,
            valid=True,
            status='00')
        if result.rowcount:
            await api.writeLog(app=app, fileid=fileid, option='00', conn=conn)
            return web.json_response({'result': True, 'message': '文件上传成功'})
        else:
            os.remove(filename)
            return web.json_response({'result': False, 'message': '文件上传失败'})


@routes.post('/app/disable', True)
async def disable(app, files):
    if not isinstance(files, list):
       return web.json_response({'result': False, 'message': '参数files非list'})
    if len(files) <=0:
       return web.json_response({'result': False, 'message': '未选择要设置无效的文件'}) 
    async with app['db'].acquire() as conn:
        cursor = await conn.execute(Filelist
        .update()
        .where(Filelist.c.fileid.in_(files))
        .values(status = '12'))
        return web.json_response({'result': True, 'message': '设置文件无效成功：%d个' %cursor.rowcount})


@routes.post('/app/sendlink', True)
async def sendLink(app, files, email):
    if not isinstance(files, list):
       return web.json_response({'result': False, 'message': '参数files非list'})
    if len(files) <=0:
       return web.json_response({'result': False, 'message': '未选择要送的文件'})
    
    # 更新Filelist表中状态01-已发送和文件的md5
    async with app['db'].acquire() as conn:
        cursor = await conn.execute(Mail.select().where(Mail.c.uid == app['uid']))
        row = await cursor.fetchone()
        if row is None:
            return web.json_response({'result': False, 'message': '用户发送邮箱未设置'})
        # 生成文件的md5
        urls = []
        for fileid in files:
            filemd5 = hashlib.md5(fileid.encode('utf-8')).hexdigest()
            urls.append('http://%s:%d/download/%s' % (app['host'], app['port'], filemd5))
            await conn.execute(Filelist.update().where(Filelist.c.fileid == fileid)
                               .values(status = '01', filemd5 = filemd5))
            await api.writeLog(app=app, fileid=fileid, option='02', conn=conn)
        content = '\n'.join(urls)
        password = api.decryptADS(app['config'].mail.seckey, row.password)
        mail = api.sendMail(content, row.subject, row.mail, email, password)
        if mail.get('result'):
            return web.json_response({'result': True, 'message': '发送链接成功'})
        else:
            return web.json_response({'result': False, 'message': mail.get('message')})


@routes.get('/download/{id}')
async def download(app, id):
    async with app['db'].acquire() as conn:
        cursor = await conn.execute(Filelist.select().where(Filelist.c.filemd5 == id))
        row = await cursor.fetchone()
        if row is None:
            return web.Response(text='文件链接有误')
        # 检查文件状态
        if row.status == '10':
            return web.Response(text='文件下载次数超限')
        if row.status == '11':
            return web.Response(text='文件已过期')
        if row.status == '12':
            return web.Response(text='文件下载已限制')
        # 检查文件是否过期
        date = datetime.date.today()
        if date > row.validity:
            print('date > row.validity')
            await conn.execute(Filelist.update().where(Filelist.c.fileid == row.fileid).values(status = '11'))
            await api.writeLog(app=app, fileid=row.fileid, option='12', conn=conn)
            return web.Response(text='文件已过期')
        filename = os.path.join(app['config'].web.path, row.fileid)
        if not os.path.exists(filename):
            return web.Response(text='文件不存在')
        res = web.FileResponse(filename)
        res.enable_compression()
        # 检查下载次数是否超限
        count = row.download + 1
        if count >= row.limit:
            status = '10'
            await api.writeLog(app=app, fileid=row.fileid, option='11', conn=conn)
        else:
            status = row.status
        await conn.execute(Filelist.update().where(Filelist.c.fileid == row.fileid)
                           .values(download=count, status=status))
        await api.writeLog(app=app, fileid=row.fileid, option='01', conn=conn)
        return res


@routes.get('/root/mail', True)
async def getMail(app):
    async with app['db'].acquire() as conn:
        cursor = await conn.execute(Mail.select().where(Mail.c.uid == app['uid']))
        row = await cursor.fetchone()
        if row:
            data = {'mail': row.mail, 'password': None, 'subject': row.subject}
            return web.json_response({'result': True, 'row': data})
        else:
            return web.json_response({'result': False})


@routes.post('/root/mail', True)
async def updateMail(app, mail, password, subject):
    auth = api.authSMTP(mail, password)
    if not auth.get('result'):
        return web.json_response({'result': False, 'message': auth.get('message')})
    async with app['db'].acquire() as conn:
        ads_pwd = api.encryptADS(app['config'].mail.seckey, password)
        cursor = await conn.execute(Mail.select().where(Mail.c.uid == app['uid']))
        row = await cursor.fetchone()
        print(row)
        if row:
            cursor = await conn.execute(Mail.update().where(Mail.c.uid==app['uid'])
                    .values(mail=mail, password=ads_pwd, subject=subject))
            if cursor.rowcount == 1:
                return web.json_response({'result': True, 'message': '电子邮件更新成功'})
            else:
                return web.json_response({'result': False, 'message': '电子邮件更新失败'})
        else:
            cursor = await conn.execute(Mail.insert(),
                     uid=app['uid'], mail=mail, password=ads_pwd, subject=subject)
            if cursor.rowcount == 1:
                return web.json_response({'result': True, 'message': '电子邮件新增成功'})
            else:
                return web.json_response({'result': False, 'message': '电子邮件新增失败'})


@routes.post('/app/save', True)
async def save(app, fileid, fileaut, validity, getcode, limit):
    async with app['db'].acquire() as conn:
        cursor = await conn.execute(Filelist.update().where(Filelist.c.fileid == fileid)
                       .values(fileaut=fileaut, validity=validity, getcode=getcode, limit=limit))
        if cursor.rowcount == 1:
            await api.writeLog(app=app, fileid=fileid, option='10', conn=conn)
            return web.json_response({'result': True, 'message': '文件%s设置保存成功' %fileid})
        else:
            return web.json_response({'result': False, 'message': '文件%s设置保存失败' %fileid})

@routes.post('/app/logs', True)
async def logs(app, fileid):
    async with app['db'].acquire() as conn:
        cursor = await conn.execute(Filelog.select().where(Filelog.c.fileid==fileid))
        rows = await cursor.fetchall()
        data = []
        if rows:
            for row in rows:
                row = dict(row)
                row['create_time'] = row['create_time'].strftime('%Y-%m-%d %H:%M:%S')
                data.append(row)
        else:
            data = []
        return web.json_response(data=data)