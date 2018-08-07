# coding: utf-8
from atomos import atomic
from concurrent.futures import ThreadPoolExecutor

from mirror.libs import components
from mirror.scheduler.schuduler import MysqlScheduler
from mirror.downloader.downloader import Downloader
from mirror.processor.processor import PageProcessor
from mirror.pipeline.pipeline import LocalFilePipeline

STAT_INIT = 0
STAT_RUNNING = 1
STAT_STOPPED = 2


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

        self._site = components.create_site()
        self._stat = atomic.AtomicInteger(STAT_INIT)
        self._threadPool = ThreadPoolExecutor()

    def check_running_stat(self):
        while True:
            stat_now = self._stat.get()
            if stat_now == STAT_RUNNING:
                raise components.SpiderException("Spider is already running")
            if self._stat.compare_and_set(stat_now, STAT_RUNNING):
                break

    def init_component(self):
        """
            初始化各个组件
        """
        if self.scheduler is None:
            self.scheduler = MysqlScheduler(self)
        if self.downloader is None:
            self.downloader = Downloader(self)
        if self.processor is None:
            self.processor = PageProcessor(self)
        if not self.pipelines:
            self.pipelines = [LocalFilePipeline(self)]
        if self._threadPool is None:
            self._threadPool = ThreadPoolExecutor()

    def init_start_requests(self):
        start_urls = self._site.get_start_urls()
        if start_urls:
            start_requests = list()
            for url in start_urls:
                request = components.Request(url)
                start_requests.append(request)
            for request in start_requests:
                self.scheduler.push(self, request)

    def run(self):
        # 检测当前运行状态
        self.check_running_stat()
        # 初始化各个组件
        self.init_component()
        # 初始化请求队列
        self.init_start_requests()

        while self._stat == STAT_INIT:
            # 获取request
            request = self.scheduler.poll()

            def runner():
                # 下载内容
                page = self.downloader.download(request)
                if page is None:
                    return
                # 解析网页
                self.processor.process(page)
                # 获取解析后的结果
                result_items = page.get_result_items()
                if result_items is None:
                    return
                # 获取目标结果
                for new_req in page.get_target_requests():
                    self.scheduler.push(new_req)
                # 处理下载后的结果
                for pipeline in self.pipelines:
                    pipeline.process(result_items)

            # 运行
            self._threadPool.submit(runner)
        self._stat.set(STAT_STOPPED)

    def get_site(self):
        return self._site

    def get_uuid(self):
        return self._site.get_key()
