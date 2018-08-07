# coding: utf-8

from urllib.parse import urljoin

from pyquery import PyQuery as pq


class PageProcessor:

    def __init__(self, task):
        self.task = task
        self.task_key = self.task.get_uuid()

    def _abs_url(self, origin_url, url):
        """
        重新构造url，过滤掉无效的字符
        :param origin_url:
        :param url:
        :return:
        """
        if url.startswith('#'):
            return
        target_url = urljoin(origin_url, url)
        if '#' in target_url:
            pos = target_url.find('#')
        return target_url

    def process(self, page):
        """
        :type page: mirror.libs.components.Page
        """
        # 仅解析html页面
        if 'text/html' != page.content_type:
            return
        query = pq(page.text)

        for tag in query('*'):
            # href or src
            target_url = tag.get('href')
            if not target_url:
                target_url = tag.get('src')
            # 生成绝对的url
            target_url = self._abs_url(page.url, target_url)

        # 提取所有的url

        # 组合成合适的url

        # 过滤掉不属于当前网站的url
