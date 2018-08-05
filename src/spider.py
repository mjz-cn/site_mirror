# coding: utf-8
import threading
from atomos import atomic
from concurrent.futures import ThreadPoolExecutor

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
        #
        self.scheduler = None
        self.pipelines = None
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
            # 获取request
            request = self.scheduler.poll()
            # 生成runner
            runner = _generate_runner(self, request)
            # 运行
            self.threadPool.submit(runner)
        self.stat.set(STAT_STOPPED)


