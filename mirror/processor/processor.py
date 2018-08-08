# coding: utf-8

from pyquery import PyQuery as pq

from mirror.libs.components import Request
from mirror.libs import tools


class PageProcessor:

    def __init__(self, task):
        self.task = task
        self.task_domain = tools.get_domain(task.get_site().domain)
        self.task_key = self.task.get_uuid()

    def get_target_request(self, page, target_url):
        """
        重新构造url，过滤掉无效的字符
        """
        if not target_url:
            return
        target_url = tools.abs_url(page.url, target_url)
        # 删除fragment
        target_url = tools.delete_fragment(target_url)
        # 检测url域名是否与当前网站域名一致
        if not target_url or not tools.has_same_domain(self.task_domain, target_url):
            return
        return Request(target_url)

    def process(self, page):
        """
        :type page: mirror.libs.components.Page
        """
        # 仅解析html页面
        if not tools.is_html(page.content_type):
            return
        query = pq(page.text)
        for tag in query('*'):
            # href or src
            target_url = tag.get('href')
            if not target_url:
                target_url = tag.get('src')
            # 生成目标request
            target_request = self.get_target_request(page, target_url)
            if target_request:
                page.add_target_request(target_request)
