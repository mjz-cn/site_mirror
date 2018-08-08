# coding: utf-8
import logging
import os

from pyquery import PyQuery

from mirror.libs import tools


class LocalFilePipeline:
    """
        将下载的内容保存到本地对应的文件中, 并将网页中相应的url替换成本地url
    """

    def __init__(self, task):
        self.logger = logging.getLogger(LocalFilePipeline.__name__)
        self.task = task
        self.site = task.get_site()
        self.task_key = self.task.get_uuid()
        self.task_domain = tools.get_domain(task.get_site().domain)

    def to_file_path(self, url):
        """
        将url转换为本地的文件路径，用于存储
        """
        if url.endswith('/'):
            url += 'index.html'
        if '://' in url:
            pos = url.find('/')
            url = url[pos + 2:]
        dires = url.split('/')
        path = self.site.storage_path
        for dire in dires:
            path = os.path.join(path, dire)
        return path

    def filter_query(self, page, url):
        url = tools.abs_url(page.url, url)
        mu = tools.MutableUrl(url)
        if mu.query:
            li = mu.path.split('/')
            name = li[-1]
            name = tools.md5(mu.query) + name
            li[-1] = name
            mu.path = '/'.join(li)
            mu.query = ''
            url = mu.to_new_url()
        return url

    def to_local_url(self, page, url):
        """
        将url转换为本地的url
        :param url: url为包含域名的完整的URL
        """
        # 过滤掉其它域名的URL
        if not tools.has_same_domain(self.task_domain, url):
            return
        # 网页中的路径转换成本地的路径

        if '://' in url:
            if url.startswith(self.task_domain):
                url = url.replace(self.task_domain, '')
                cnt = page.url.count('/') - 3
                for i in range(cnt):
                    url = '../' + url
        if url.startswith('/'):
            url = '.' + url
        return url

    def reconstruct_data(self, page):
        """
        将page中的URL替换成本地对应的URL
        :type page: mirror.libs.components.Page
        """
        # 仅处理html页面中的URL
        if not tools.is_html(page.content_type):
            return page.raw_content
        # 解析页面，替换其中所有的url
        page_query = PyQuery(page.text)
        # 替换所有的href, src
        for tag in page_query('*'):
            # 判断是否含有href, src
            tag = PyQuery(tag)
            attr_name = 'href'
            url = tag.attr(attr_name)
            if not url:
                attr_name = 'src'
                url = tag.attr(attr_name)
            # 过滤参数
            url = self.filter_query(page, url)
            if url:
                url = self.to_local_url(page, url)
            tag.attr(attr_name, url)

        return page_query.outer_html().encoding(page.encoding)

    def process(self, page):
        """
        将数据保存到本地
        :param page:
        :return:
        """
        file_path = self.to_file_path(page.url)
        raw_data = self.reconstruct_data(page)
        # 存储
        with open(file_path, 'wb') as fd:
            fd.write(raw_data)
            self.logger.info("storage a file, url:{}, file_path:{}".format(page.url, file_path))
