# coding: utf-8

from peewee import *

from config.config import global_config

database = MySQLDatabase('mirror', **{'charset': 'utf8',
                                      'use_unicode': True,
                                      'host': global_config.get('mysql::host'),
                                      'user': global_config.get('mysql::user'),
                                      'password': global_config.get('mysql::password'),
                                      }
                         )
# mysql事务问题
database.connect_params['autocommit'] = True


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class RequestQueue(BaseModel):
    request_json = CharField(constraints=[SQL("DEFAULT ''")])
    task_key = CharField(index=True)
    id = IntegerField(index=True)

    class Meta:
        table_name = 't_request_queue'


class UrlDuplicateCheck(BaseModel):
    id = IntegerField(index=True)
    task_key = CharField(index=True)
    url_md5 = CharField(constraints=[SQL("DEFAULT ''")])
    url = CharField(constraints=[SQL("DEFAULT ''")])
    origin_url = CharField()

    class Meta:
        table_name = 't_url_duplicate_check'
        indexes = (
            (('task_key', 'url_md5'), True),
        )
