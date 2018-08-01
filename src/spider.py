# coding: utf-8
import threading
from atomos import atomic
from concurrent.futures import ThreadPoolExecutor


STAT_INIT = 0
STAT_RUNNING = 1
STAT_STOPPED = 2

class Spider:
    """
        组合其它组件来完成下载任务
    """

    def __init__(self):
        #
        self.scheduler = None
        self.pipeline = None
        self.downloader = None
        self.processor = None
        self.stat = atomic.AtomicInteger(STAT_INIT)
        self.threadPool = ThreadPoolExecutor()

    def run(self):
        pass
        # 检测当前运行状态
        # 初始化各个组件
        # 初始化请求队列
        # 开始运行

        while self.stat == STAT_INIT:
            # 弹出request
            request = self.scheduler.poll()
