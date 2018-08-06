# coding: utf-8

import json

from mirror.models.models import UrlDuplicateCheck, RequestQueue
from mirror.libs.components import Request


class MysqlScheduler:

    def __init__(self):
        pass
        # 获取mysql配置

    def poll(self, spider):
        """
            弹出最新的url
        """
        query = RequestQueue.select()
        query.where(RequestQueue.task_key == spider.get_uuid())
        query.order_by(RequestQueue.id.desc())
        query.limit(1)
        request_queue = query.get()
        if request_queue is None:
            return None
        request_queue.delete_instance()
        return Request.create(request_queue.request_json)


    def push(self, spider, request):
        """
            压入未访问过的request
        """
        request_queue = RequestQueue()
        request_queue.task_key = spider.get_uuid()
        request_queue.request_json = request.to_json()
        request_queue.save()

    def is_visited(self, request):
        """
            仅判断request是否被访问过
        """
        pass

    def is_duplicate(self, spider, request):
        """
            判断request是否被访问过，如果没有则插入已访问过的的队列中
        """
        pass
