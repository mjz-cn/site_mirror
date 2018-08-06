# coding: utf-8
import json

import requests


class SpiderException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)

        self.errors = errors


class Request:

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

    def __init__(self, url):
        self.request = None
        self.response = None
        # 当前页面产出的目标request
        self.targetRequests = set()

    def add_target_request(self, request):
        self.targetRequests.add(request)


class SiteConfig:
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
        # cookie
        self.cookies = dict()
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


def create_site_config():
    return SiteConfig()