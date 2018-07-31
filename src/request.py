# coding: utf-8


class Request:

    def __init__(self):
        self.url = None
        self.extras = dict()

    def put_extra(self, key, value):
        self.extras[key] = value
        return self

    def get_extra(self, key):
        return self.extras[key]
