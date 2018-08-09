# coding: utf-8

import json
import logging

import peewee

from mirror.models import models
from mirror.libs import tools
from mirror.models.models import UrlDuplicateCheck, RequestQueue
from mirror.libs.components import Request


class MysqlScheduler:

    def __init__(self, task):
        self.logger = logging.getLogger(MysqlScheduler.__name__)
        self.task = task
        self.task_key = self.task.get_uuid()

    def poll(self):
        """
            弹出最新的url
        """
        try:
            request_queue = RequestQueue.select().where(RequestQueue.task_key == self.task_key).order_by(
                RequestQueue.id.desc()).limit(1).get()
        except models.DoesNotExist as e:
            self.logger.warning("Has no new request")
            request_queue = None

        if request_queue is None:
            return None
        request_queue.delete_instance()
        return Request.create(request_queue.request_json)

    def push(self, request):
        """
            压入未访问过的request
        """
        if self.is_duplicate(request):
            return False
        self.logger.debug("push to queue, url: " + request.url)
        r = RequestQueue.insert(task_key=self.task_key, request_json=request.to_json()).execute()
        return True

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
        try:
            UrlDuplicateCheck.insert(task_key=self.task_key, url_md5=tools.md5(request.url)).execute()
        except peewee.IntegrityError as e:
            self.logger.info("Duplicate url " + str(e))
            return True
        return False
