# coding: utf-8
import logging
import threading

from atomos import atomic
from concurrent.futures import ThreadPoolExecutor
import time

from mirror.libs import components, tools
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

    def __init__(self, site):
        self.logger = logging.getLogger(Spider.__name__)
        # 运行组件
        self.scheduler = None
        self.pipelines = None
        self.downloader = None
        self.processor = None

        self._site = site
        self._stat = atomic.AtomicInteger(STAT_INIT)
        self._new_url_lock = threading.RLock()
        self._new_url_condition = threading.Condition(self._new_url_lock)
        self._threadPool = tools.CountableThreadPool(site.thread_cnt, site.key)

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
        start_urls = self._site.start_urls
        if start_urls:
            start_requests = list()
            for url in start_urls:
                request = components.Request(url, url, self._site.charset)
                start_requests.append(request)
            for request in start_requests:
                self.scheduler.push(request)
        else:
            self.logger.warning("Spider has no start urls")

    def stop(self):
        if self._stat.compare_and_set(STAT_RUNNING, STAT_STOPPED):
            self.logger.info("Stop spider success")
        else:
            self.logger.info("Stop spider fail. Stat: " + str(self._stat))

    def run(self):
        # 检测当前运行状态
        self.check_running_stat()
        # 初始化各个组件
        self.init_component()
        # 初始化请求队列
        self.init_start_requests()
        self.logger.info("Start to run spider")
        while self._stat.get() == STAT_RUNNING:
            # 获取request
            request = self.scheduler.poll()
            if self._site.sleep_time:
                time.sleep(self._site.sleep_time / 1000)

            if request is None:
                # 如果没有新的request并且没有正在执行的线程，则表示本次任务执行完成
                if self._threadPool.get_thread_alive() == 0:
                    self.logger.info("Complete spider task!")
                    break
                self.wait_new_url()
            else:
                def new_runner(req):
                    def runner():
                        try:
                            self.logger.info("Begin to handle request, url:" + req.url)
                            # 下载内容
                            page = self.downloader.download(req)
                            if page is None:
                                return
                            # 解析网页
                            self.processor.process(page)
                            # 获取目标结果
                            for new_req in page.target_requests:
                                self.scheduler.push(new_req)

                            # 处理下载后的结果
                            for pipeline in self.pipelines:
                                pipeline.process(page)

                        except Exception as e:
                            self.logger.error("Process request error, url: {}, exception: {}".format(req.url, e))
                            raise e
                        finally:
                            self.signal_new_url()
                    return runner
                self._threadPool.submit(new_runner(request))
        self._stat.set(STAT_STOPPED)

    def wait_new_url(self):
        with self._new_url_lock:
            self._new_url_condition.wait()

    def signal_new_url(self):
        with self._new_url_lock:
            self._new_url_condition.notify_all()

    def get_site(self):
        return self._site

    def get_uuid(self):
        return self._site.key
