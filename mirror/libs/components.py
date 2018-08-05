# coding: utf-8
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


class Page:

    def __init__(self, url):
        self.request = None
        self.response = None
        # 当前页面产出的目标request
        self.targetRequests = set()

    def add_target_request(self, request):
        self.targetRequests.add(request)
