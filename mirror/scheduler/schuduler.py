# coding: utf-8


class Scheduler:

    def __init__(self):
        pass

    def poll(self, spider):
        """
            弹出最新的url
        """
        pass

    def push(self, spider, request):
        """
            压入未访问过的request
        """
        pass

    def is_visited(self, request):
        """
            仅判断request是否被访问过
        """
        pass

    def is_duplicate(self, spider, request):
        """
            判断request是否被访问过，如果没有则插入已访问过的的队列中
        :param spider:
        :param request:
        :return:
        """
        pass
