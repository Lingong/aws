# --------------------------------------------------------------------------------
# 文件：orm.py
# 描述：该源码为数据库和对象的关联对应模块
# 版本：0.1
# 作者：lg
# 日期：2020.01.15
# 修改：2020.01.15 0.1 lg  新增版本
# --------------------------------------------------------------------------------


import logging
import re
from .db import Database

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


class Field(object):
    def __init__(self, field_name, field_type, primary_key, default):
        self.field_name = field_name
        self.field_type = field_type
        self.primary_key = primary_key
        self.default = default


class Varchar(Field):
    def __init__(self, field_name=None, primary_key=False, default=None, length=100):
        super().__init__(field_name, 'varchar(%d)' % length, primary_key, default)


class Char(Field):
    def __init__(self, field_name=None, primary_key=False, default=None, length=100):
        super().__init__(field_name, 'char(%d)' % length, primary_key, default)


class Text(Field):
    def __init__(self, field_name=None, primary_key=False, default=None):
        super().__init__(field_name, 'text', primary_key, default)


class Date(Field):
    def __init__(self, field_name=None, primary_key=False, default=None):
        super().__init__(field_name, 'date', primary_key, default)


class Time(Field):
    def __init__(self, field_name=None, primary_key=False, default=None):
        super().__init__(field_name, 'time', primary_key, default)


class Timestamp(Field):
    def __init__(self, field_name=None, primary_key=False, default=None):
        super().__init__(field_name, 'timestamp', primary_key, default)


class Smallint(Field):
    def __init__(self, field_name=None, primary_key=False, default=0):
        super().__init__(field_name, 'smallint', primary_key, default)


class Integer(Field):
    def __init__(self, field_name=None, primary_key=False, default=0):
        super().__init__(field_name, 'integer', primary_key, default)


class Bigint(Field):
    def __init__(self, field_name=None, primary_key=False, default=0):
        super().__init__(field_name, 'bigint', primary_key, default)


class Money(Field):
    def __init__(self, field_name=None, primary_key=False, default=0.00):
        super().__init__(field_name, 'money', primary_key, default)


class Numeric(Field):
    def __init__(self, field_name=None, primary_key=False, default=0.0, length=10, precision=2):
        super().__init__(field_name, 'numeric(%d,%d)' %(length, precision), primary_key, default)


class Double(Field):
    def __init__(self, field_name=None, primary_key=False, default=0.00):
        super().__init__(field_name, 'double precision', primary_key, default)


class Real(Field):
    def __init__(self, field_name=None, primary_key=False, default=0.00):
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
            ['%s' % mapping[field].field_name for field in fields])
        str_values = ','.join(['?'] * len(mapping))
        str_create = ','.join(
            ['%s %s' % (field, mapping[field].field_type) for field in fields])
        str_keys = ','.join(['%s' % primarykey for primarykey in primarykeys])

        if len(primarykeys) == 0:
            attrs['__primary_key__'] = None
        else:
            attrs['__primary_key__'] = primarykeys
        attrs['__mapping__'] = mapping
        attrs['__table__'] = tablename
        attrs['__fields__'] = fields
        attrs['__default__'] = default
        attrs['__select__'] = 'select %s from %s ' % (str_fields, tablename)
        attrs['__insert__'] = 'insert into %s(%s) values(%s)' % (
            tablename, str_fields, str_values)
        attrs['__update__'] = 'update %s set ' % tablename
        attrs['__delete__'] = 'delete from %s' % tablename
        attrs['__create__'] = 'create table %s(%s,primary key(%s))' % (
            tablename, str_create, str_keys)
        attrs['__drop__'] = 'drop table %s' % tablename
        attrs['__count__'] = 'select count(*) from %s ' % tablename
        return type.__new__(cls, name, base, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    async def chain(cls, where=None, args=None):
        rest = await cls.read(where=where, args=args, limit=1)
        if rest:
            return rest[0]
        else:
            return None

    @classmethod
    async def count(cls, where=None, args=None):
        sql = cls.__count__
        args = format_args(where, args)
        if where:
            sql += ' where ' + where
        return await Database.select(sql=sql, args=args, limit=1)[0][0]

    @classmethod
    async def read(cls, where=None, args=None, order=None, limit=None, offset=None):
        sql = cls.__select__
        args = format_args(where, args)
        if where:
            sql += ' where ' + format_fields(where, cls.__fields__)
        if order:
            sql += ' order by ' + format_fields(order, cls.__fields__)
        rset = []
        async for row in Database.select(sql, args, limit, offset):
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

    async def save(self):
        mapping = self.__mapping__
        sql = self.__insert__
        args = []
        for field in self.__fields__:
            if hasattr(self, field):
                args.append(self[field])
            else:
                args.append(mapping[field].default)
        args = tuple(args)
        return await Database.change(sql, args)

    async def update(self, where, args):
        args = format_args(where, args)
        sql = self.__update__
        sql += ','.join('[%s]=?' % key for key in self.keys())
        argsset = [vaule for vaule in self.values()]
        argsset.extend(list(args))
        argsset = tuple(argsset)
        if where:
            sql += ' where %s ' % format_fields(where, self.__fields__)
        return await Database.change(sql, argsset)

    @classmethod
    async def delete(cls, where=None, args=None):
        sql = cls.__delete__
        args = format_args(where, args)
        if where:
            sql += ' where %s' % format_fields(where, cls.__fields__)
        return await Database.change(sql, args)

    @classmethod
    async def create(cls):
        sql = cls.__create__
        await Database.change(sql)

    @classmethod
    async def drop(cls):
        sql = cls.__drop__
        await Database.change(sql)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value
