# coding: utf-8


class PageProcessor:

    def __init__(self, task):
        self.task = task
        self.task_key = self.task.get_uuid()

    def process(self, page):
        pass
        # 提取所有的url
        # 组合成合适的url
        # 过滤掉不属于当前网站的url
