# coding: utf-8

import json

from mirror.libs import tools
from mirror.models.models import UrlDuplicateCheck, RequestQueue
from mirror.libs.components import Request


class MysqlScheduler:

    def __init__(self, task):
        self.task = task
        self.task_key = self.task.get_uuid()

    def poll(self):
        """
            弹出最新的url
        """
        query = RequestQueue.select()
        query.where(RequestQueue.task_key == self.task_key)
        query.order_by(RequestQueue.id.desc())
        query.limit(1)
        request_queue = query.get()
        if request_queue is None:
            return None
        request_queue.delete_instance()
        return Request.create(request_queue.request_json)

    def push(self, request):
        """
            压入未访问过的request
        """
        request_queue = RequestQueue()
        request_queue.task_key = self.task_key
        request_queue.request_json = request.to_json()
        request_queue.save()

    def is_visited(self, request):
        """
            仅判断request是否被访问过
        """
        if request is None:
            return True
        url_md5 = tools.md5(request.url)
        return UrlDuplicateCheck.select().where(UrlDuplicateCheck.task_key == self.task_key,
                                         UrlDuplicateCheck.url_md5 == url_md5).exists()

    def is_duplicate(self, request):
        """
            判断request是否被访问过，如果没有则插入已访问过的的队列中
        """
        UrlDuplicateCheck.insert(task_key = self.task_key, url_md5 = tools.md5(request.url)).execute()
        return True