# coding: utf-8
import json

import requests

from config.config import global_config


class SpiderException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)

        self.errors = errors


class Request:
    STATUS_CODE = 'status_code'
    CYCLE_TRIED_TIMES = "_cycle_tried_times"

    def __init__(self, url):
        self.url = url
        self.extras = dict()
        self.request = None

    def put_extra(self, key, value):
        self.extras[key] = value
        return self

    def get_extra(self, key):
        return self.extras[key]

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def create(j):
        r = Request(None)
        r.__dict__ = json.loads(j)
        return r


class Page:
    """
    对一次请求和请求结果的封装
    """

    def __init__(self, request, response=None):
        """
        :type request: mirror.libs.components.Request
        :type response: requests.Response
        """
        self.request = request
        self.response = response
        self._content_type = None

        # 当前页面产出的目标request
        self.targetRequests = set()

    def add_target_request(self, request):
        self.targetRequests.add(request)

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def raw_content(self):
        return self.response.content

    @property
    def url(self):
        return self.request.url

    @property
    def text(self):
        return self.response.text

    @property
    def encoding(self):
        return self.response.encoding

    @property
    def content_type(self):
        if self._content_type:
            return self._content_type
        headers = self.response.headers
        tokens = headers.get('content-type').strip().split(';')
        content_type, params = tokens[0].strip(), tokens[1:]
        self._content_type = content_type
        return self._content_type


class Site:
    """
        对网站的抽象
    """

    def __init__(self):
        # 网站域名
        self.domain = None
        # 线程数量
        self.thread_cnt = 0
        # http user-agent
        self.user_agent = None
        # 默认cookie
        self.default_cookies = dict()
        # 网站编码
        self.charset = "utf-8"
        #
        self.sleep_time = 0
        # 超时
        self.time_out = 0
        # 重试次数
        self.retry_times = 0
        # 重试间隔
        self.retry_sleep_time = 0
        self.storage_path = ''
        self.key = ''

    def accept(self, page):
        """
        判断是否接受此page, 根据status_code
        :param page: Page
        """
        return True


def _set(site, name, value):
    if value:
        setattr(site, name, value)


def create_site():
    """
    :rtype: Site
    """
    site = Site()
    _set(site, 'domain', global_config.get('site::domain'))
    _set(site, 'thread_cnt', global_config.get('site::thread_cnt'))
    _set(site, 'user_agent', global_config.get('site::user_agent'))
    _set(site, 'default_cookies', global_config.get('site::default_cookies'))
    _set(site, 'charset', global_config.get('site::charset'))
    _set(site, 'sleep_time', global_config.get('site::sleep_time'))
    _set(site, 'time_out', global_config.get('site::time_out'))
    _set(site, 'retry_times', global_config.get('site::retry_times'))
    _set(site, 'retry_sleep_time', global_config.get('site::retry_sleep_time'))
    _set(site, 'storage_path', global_config.get('site::storage_path'))
    _set(site, 'key', global_config.get('site::key'))
    return Site()
