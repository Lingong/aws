# --------------------------------------------------------------------------------
# 文件：orm.py
# 描述：该源码为数据库和对象的关联对应模块
# 版本：1.7
# 作者：lg
# 日期：2016.11.11
# 修改：2016.11.11 0.1 lg  新增版本
#      2016.11.17 0.2 lg  修改connect的入口参数默认值，修改方法create,drop
#      2016.11.19 0.3 lg  修改多个方法
#      2016.11.19 0.4 lg  修改read
#      2016.12.01 0.5 lg  修复create语句的BUG
#      2016.12.04 0.6 lg  增加组合主键功能
#      2017.02.06 0.7 lg  修改chain功能
#      2017.02.08 0.8 lg  修改connect异常处理流程和修改execute_dml
#      2017.02.22 0.9 lg  修复execute_dml,chain的bug
#      2017.04.13 1.0 lg  修改read和chain方法，如果结果集为空时，返回None
#      2017.04.19 1.1 lg  删除pypyodbc,增加类函数count,去除logging
#      2017.04.22 1.2 lg  修改类Connect
#      2017.05.04 1.3 lg  增加分页查询功能
#      2017.05.23 1.4 lg  修复create方法的BUG
#      2017.07.09 1.5 lg  为字段名增加[]，以便处理字段名为关键字的情况。
#      2018.11.13 1.6 lg  修改execute_query，Connect，execute_dml异常处理模块
#      2020.01.08 1.7 lg  分离数据库sqlite3
# --------------------------------------------------------------------------------

import logging
import re
import sqlite3

# 以字母开头，只能包含字母、数字和下划线，长度大于1小于254个字符
re_field = re.compile(r'^[a-zA-Z]\w*')

# 字母、数字和下划线
re_flag = re.compile(r'[0-9a-zA-Z_]')

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(module)s.%(funcName)s[line:%(lineno)d] %(levelname)s:%(message)s',
    datefmt='%Y%m%d %H:%M:%S')


def format_args(where, args):
    if args is None:
        args = ()

    if isinstance(args, list):
        args = tuple(args)

    if not isinstance(args, tuple):
        raise ValueError('args参数不是元组或者列表:%s' % args)

    if len(args) > 0 and where is None:
        raise ValueError('查询条件为空，参数也必须为空')

    if where:
        count = where.count('?')
        if count == 0:
            raise ValueError('查询条件中必须有？占位符')
        elif count != len(args):
            raise ValueError('查询条件中站位符？与参数个数不符')

    return args


def format_fields(fields_str, fields):
    fmt_str = fields_str
    len_str = len(fields_str)
    for field in fields:
        pos = fields_str.find(field)
        ln = len(field)
        if pos > -1:
            # 判断子串左边是否为字母、数字和下划线
            if pos > 0:
                if re_flag.match(fields_str[pos - 1]):
                    continue
            # 判断子串右边是否为字母、数字和下划线
            if pos + ln < len_str:
                if re_flag.match(fields_str[pos + ln]):
                    continue
            fmt_str = fmt_str.replace(field, '[' + field + ']')
    return fmt_str


class Connect(object):
    dbname = None

    @classmethod
    def connect(cls):
        try:
            if cls.dbname is None:
                raise ValueError('数据库文件未设置')
            conn = sqlite3.connect(cls.dbname)
            return conn
        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError('数据库连接失败：%s' % e)

    @classmethod
    def execute_ddl(cls, sql=None):
        if sql is None:
            raise ValueError('sql执行语句为空')
        conn = cls.connect()
        cur = conn.cursor()
        logging.info('[ %s ]' % sql)
        try:
            cur.execute(sql)
        except sqlite3.OperationalError as e:
            cur.close()
            conn.close()
            raise sqlite3.OperationalError('执行SQL失败：%s' % e)
        cur.close()
        conn.close()

    @classmethod
    def execute_dml(cls, sql=None, args=None):
        conn = cls.connect()
        cur = conn.cursor()
        logging.info('[ %s %s ]' % (sql, args))
        try:
            cur.execute(sql, args)
        except sqlite3.OperationalError as e:
            conn.rollback()
            cur.close()
            conn.close()
            raise sqlite3.OperationalError('数据库执行失败：%s' % e)
        conn.commit()
        cur.close()
        conn.close()
        return cur.rowcount

    @classmethod
    def execute_query(cls, sql=None, args=None, limit=None, offset=None):
        if isinstance(limit, int) and limit < 1:
            raise ValueError('查询条数不能小于1')
        if not isinstance(limit, int) and limit:
            raise ValueError('参数limit类型非法')

        if isinstance(offset, int) and offset < 0:
            raise ValueError('跳过条数不能小于0')
        if not isinstance(offset, int) and offset:
            raise ValueError('参数offset类型非法')

        if offset and limit is None:
            raise ValueError('跳过条数不为空时，查询条数不能为空')

        if limit:
            sql = '%s limit %d' % (sql, limit)
        if offset:
            sql = '%s offset %d' % (sql, offset)
        logging.info('[ %s %s ]' % (sql, args))
        conn = Connect.connect()
        cur = conn.cursor()
        try:
            cur.execute(sql, args)
        except sqlite3.OperationalError as e:
            cur.close()
            conn.close()
            raise sqlite3.OperationalError('[ 数据库执行失败：%s ]' % e)
        rest = cur.fetchall()
        cur.close()
        conn.close()
        return rest


class Field(object):
    def __init__(self, field_name, field_type, primary_key, default):
        self.field_name = field_name
        self.field_type = field_type
        self.primary_key = primary_key
        self.default = default


class String(Field):
    def __init__(self, field_name=None, primary_key=False, default=None, length=100):
        if length < 1:
            raise ValueError('字段长度不能小于1')
        if length > 4000:
            raise ValueError('字段长度不能超过4000')
        super().__init__(field_name, 'varchar(%s)' % length, primary_key, default)


class Text(Field):
    def __init__(self, field_name=None, primary_key=False, default=None):
        super().__init__(field_name, 'text', primary_key, default)


class Integer(Field):
    def __init__(self, field_name=None, primary_key=False, default=0):
        super().__init__(field_name, 'bigint', primary_key, default)


class Float(Field):
    def __init__(self, field_name=None, primary_key=False, default=0.0):
        super().__init__(field_name, 'real', primary_key, default)


class Boolean(Field):
    def __init__(self, field_name=None, primary_key=False, default=False):
        super().__init__(field_name, 'boolean', primary_key, default)


class ModelMetaclass(type):
    def __new__(cls, name, base, attrs):
        if name == 'Model':
            return type.__new__(cls, name, base, attrs)
        tablename = attrs.get('__table__') or name
        # logging.info('[ Table name: %s ]' % tablename)
        mapping = dict()
        fields = list()
        default = dict()
        primarykeys = list()
        for key, value in attrs.items():
            if isinstance(value, Field):
                if value.primary_key:
                    primarykeys.append(key)
                fields.append(key)
                if value.field_name is None:
                    value.field_name = key
                # logging.info('[ Mapping: %s -> %s ]' % (key, value.field_name))
                if not re_field.match(value.field_name):
                    raise ValueError('字段名称非法')
                mapping[key] = value
        for key in mapping.keys():
            attrs.pop(key)

        str_fields = ','.join(
            ['[%s]' % mapping[field].field_name for field in fields])
        str_values = ','.join(['?'] * len(mapping))
        str_create = ','.join(
            ['[%s] %s' % (field, mapping[field].field_type) for field in fields])
        str_keys = ','.join(
            ['[%s]' % primarykey for primarykey in primarykeys])

        if len(primarykeys) == 0:
            attrs['__primary_key__'] = None
        else:
            attrs['__primary_key__'] = primarykeys
        attrs['__mapping__'] = mapping
        attrs['__table__'] = tablename
        attrs['__fields__'] = fields
        attrs['__default__'] = default
        attrs['__select__'] = 'select %s from [%s] ' % (str_fields, tablename)
        attrs['__insert__'] = 'insert into [%s](%s) values(%s)' % (
            tablename, str_fields, str_values)
        attrs['__update__'] = 'update [%s] set ' % tablename
        attrs['__delete__'] = 'delete from [%s]' % tablename
        attrs['__create__'] = 'create table [%s](%s,primary key(%s))' % (
            tablename, str_create, str_keys)
        attrs['__drop__'] = 'drop table [%s]' % tablename
        attrs['__count__'] = 'select count(*) from [%s] ' % tablename
        return type.__new__(cls, name, base, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def chain(cls, where=None, args=None):
        rest = cls.read(where=where, args=args, limit=1)
        if rest:
            return rest[0]
        else:
            return None

    @classmethod
    def count(cls, where=None, args=None):
        sql = cls.__count__
        args = format_args(where, args)
        if where:
            sql += ' where ' + where
        return Connect.execute_query(sql, args, 1)[0][0]

    @classmethod
    def read(cls, where=None, args=None, order=None, limit=None, offset=None):
        sql = cls.__select__
        args = format_args(where, args)
        if where:
            sql += ' where ' + format_fields(where, cls.__fields__)
        if order:
            sql += ' order by ' + format_fields(order, cls.__fields__)
        rset = []
        for row in Connect.execute_query(sql, args, limit, offset):
            rs = {}
            pos = 0
            for value in row:
                rs[cls.__fields__[pos]] = value
                pos += 1
            rset.append(cls(**rs))
        if len(rset) == 0:
            return None
        else:

            return rset

    def save(self):
        mapping = self.__mapping__
        sql = self.__insert__
        args = []
        for field in self.__fields__:
            if hasattr(self, field):
                args.append(self[field])
            else:
                args.append(mapping[field].default)
        args = tuple(args)
        return Connect.execute_dml(sql, args)

    def update(self, where, args):
        args = format_args(where, args)
        sql = self.__update__
        sql += ','.join('[%s]=?' % key for key in self.keys())
        argsset = [vaule for vaule in self.values()]
        argsset.extend(list(args))
        argsset = tuple(argsset)
        if where:
            sql += ' where %s ' % format_fields(where, self.__fields__)
        return Connect.execute_dml(sql, argsset)

    @classmethod
    def delete(cls, where=None, args=None):
        sql = cls.__delete__
        args = format_args(where, args)
        if where:
            sql += ' where %s' % format_fields(where, cls.__fields__)
        return Connect.execute_dml(sql, args)

    @classmethod
    def create(cls):
        sql = cls.__create__
        Connect.execute_ddl(sql)

    @classmethod
    def drop(cls):
        sql = cls.__drop__
        Connect.execute_ddl(sql)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value
