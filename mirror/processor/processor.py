# coding: utf-8
import logging
import re

from pyquery import PyQuery as pq

from mirror.libs.components import Request, SpiderException
from mirror.libs import tools

r_url = re.compile(r'[^\w]+url\(([^)]+)\)')


class PageProcessor:

    def __init__(self, task):
        self.logger = logging.getLogger(PageProcessor.__name__)
        self.task = task
        self.task_domain = task.get_site().domain
        self.task_key = self.task.get_uuid()

    def get_target_request(self, page, origin_url):
        """
        重新构造url，过滤掉无效的字符
        """
        target_url = origin_url
        if not target_url or target_url.startswith('javascript:') or target_url.startswith('mailto:'):
            return

        target_url = tools.abs_url(page.url, target_url).strip('/')
        # 删除fragment
        target_url = tools.delete_fragment(target_url)
        # 检测url域名是否与当前网站域名一致
        if not target_url or not tools.has_same_host(self.task_domain, target_url):
            return
        return Request(target_url, origin_url)

    def process_html(self, page):
        query = pq(page.text)
        for tag in query('[href],[src]'):
            # href or src
            target_url = tag.get('href')
            if not target_url:
                target_url = tag.get('src')
            # 生成目标request
            yield target_url

    def process_css(self, page):
        css_content = page.text
        for url in r_url.findall(css_content):
            yield url

    def process(self, page):
        """
        :type page: mirror.libs.components.Page
        """
        # 仅解析html页面
        if not tools.should_process(page.content_type):
            return

        fn = None
        if tools.is_html(page.content_type):
            fn = self.process_html
        elif tools.is_css(page.content_type):
            fn = self.process_css
        else:
            self.logger.error("Do not support content_type " + page.content_type)
            raise SpiderException("Do not support content_type " + page.content_type)

        for target_url in fn(page):
            target_request = self.get_target_request(page, target_url)
            if target_request:
                page.add_target_request(target_request)
