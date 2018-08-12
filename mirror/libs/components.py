# coding: utf-8
import json

import requests

from config.config import global_config


class SpiderException(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)

        self.errors = errors


class Request:
    STATUS_CODE = 'status_code'
    CYCLE_TRIED_TIMES = "_cycle_tried_times"

    def __init__(self, url, origin_url='', charset=None):
        self.url = url
        self.origin_url = origin_url
        self.extras = dict()
        self.charset = charset

    def put_extra(self, key, value):
        self.extras[key] = value
        return self

    def get_extra(self, key):
        return self.extras[key]

    def to_json(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def create(j):
        r = Request(None, None)
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
        self._target_requests = set()
        # 从response中解析出的charset, 最优先使用
        self._header_charset = None
        self._encoding = None
        self._app_encoding = None

    def add_target_request(self, request):
        self._target_requests.add(request)

    @property
    def target_requests(self):
        return self._target_requests

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
        if self._encoding:
            return self._encoding
        if not self.response.encoding:
            return
        if self.response.encoding.lower() == 'gb2312':
            return 'gbk'
        self._encoding = self.response.encoding
        return self._encoding

    @property
    def apparent_encoding(self):
        if self._app_encoding:
            return self._app_encoding
        if not self.response.apparent_encoding:
            return
        if self.response.apparent_encoding.lower() == 'gb2312':
            return 'gbk'
        self._app_encoding = self.response.apparent_encoding
        return self._app_encoding

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
        self.headers = dict()
        # http user-agent
        self.user_agent = None
        # 默认cookie
        self._default_cookies = dict()
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
        self._start_urls = list()

    def accept(self, page):
        """
        判断是否接受此page, 根据status_code
        :param page: Page
        """
        return True

    @property
    def start_urls(self):
        return self._start_urls

    @start_urls.setter
    def start_urls(self, value):
        if type(value) == str:
            self._start_urls = [u.strip() for u in value.split(',')]
        else:
            self._start_urls = value

    @property
    def default_cookies(self):
        return self._default_cookies

    @default_cookies.setter
    def default_cookies(self, value):
        if self._default_cookies is None:
            self._default_cookies = dict()
        if type(value) == str:
            for item in value.split(','):
                key, value = item.split('=')
                self._default_cookies[key.strip()] = value.strip()
        else:
            self._default_cookies.update(value)
