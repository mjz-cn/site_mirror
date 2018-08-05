# coding: utf-8
import threading
from atomos import atomic
from concurrent.futures import ThreadPoolExecutor

import tools

STAT_INIT = 0
STAT_RUNNING = 1
STAT_STOPPED = 2


class SpiderException(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors


def _generate_runner(spider, request):
    def runner():
        # 下载内容
        page = spider.downloader.download(request, spider)
        if page is None:
            return
        # 解析网页
        spider.process(page, spider)
        # 获取解析后的结果
        result_items = page.get_result_items()
        if result_items is None:
            return
        # 获取目标结果
        for new_req in page.get_target_requests():
            spider.scheduler.push(new_req, spider)
        # 处理下载后的结果
        for pipeline in spider.pipelines:
            pipeline.process(result_items, spider)

    return runner


class Spider:
    """
        组合其它组件来完成下载任务
    """

    def __init__(self):
        # 运行组件
        self.scheduler = None
        self.pipelines = None
        self.downloader = None
        self.processor = None

        self._site = None
        self._stat = atomic.AtomicInteger(STAT_INIT)
        self._threadPool = ThreadPoolExecutor()

    def check_running_stat(self):
        while True:
            stat_now = self._stat.get()
            if stat_now == STAT_RUNNING:
                raise SpiderException("Spider is already running")
            if self._stat.compare_and_set(stat_now, STAT_RUNNING):
                break

    def init_component(self):
        """
            初始化各个组件
        """
        pass

    def init_start_requests(self):
        start_urls = self._site.get_start_urls()
        if start_urls:
            start_requests = list()
            for url in start_urls:
                request = tools.Request(url)
                start_requests.append(request)
            for request in start_requests:
                self.scheduler.push(self, request)

    def run(self):
        # 检测当前运行状态
        self.check_running_stat()
        # 初始化各个组件
        self.init_component()
        # 初始化请求队列

        # 开始运行

        while self._stat == STAT_INIT:
            # 获取request
            request = self.scheduler.poll()
            # 生成runner
            runner = _generate_runner(self, request)
            # 运行
            self._threadPool.submit(runner)
        self._stat.set(STAT_STOPPED)

    def get_site(self):
        return self._site

