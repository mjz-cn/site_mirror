# coding: utf-8
import logging
import threading

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
        self._lock = threading.Lock()

    def poll(self):
        """
            弹出最新的url
        """
        try:
            request_queue = RequestQueue.select().where(RequestQueue.task_key == self.task_key).order_by(
                RequestQueue.id.desc()).limit(1).get()
        except models.DoesNotExist as e:
            self.logger.debug("Has no new request")
            request_queue = None

        if request_queue is None:
            return None
        request_queue.delete_instance()
        request = Request.create(request_queue.request_json)
        self.logger.info("Poll request, url: " + request.url)
        return request

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
        ret = False
        try:
            UrlDuplicateCheck.insert(task_key=self.task_key, url_md5=tools.md5(request.url), url=request.url,
                                     origin_url=request.origin_url).execute()
        except peewee.IntegrityError as e:
            self.logger.debug("Duplicate url:{}, ex:{} ".format(request.url, str(e)))
            ret = True
        return ret
