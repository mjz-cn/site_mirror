# coding: utf-8


class Site:
    """
        对网站的抽象
    """

    def __init__(self):
        # 网站域名
        self.domain = None

        self.userAgent = None
        # 默认cookie
        self.defaultCookies = dict()
        # cookie
        self.cookies = dict()
        # 网站编码
        self.charset = "utf-8"
        #
        self.sleepTime = 0
        # 超时
        self.timeOut = 0
        # 重试次数
        self.retryTimes = 0
        # 重试间隔
        self.retrySleepTime = 0
