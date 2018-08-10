# coding: utf-8
import logging
import os
import threading
import re

from pyquery import PyQuery

from mirror.libs import tools

r_url = re.compile(r'[^\w]+url\(([^)]+)\)')


class LocalFilePipeline:
    """
        将下载的内容保存到本地对应的文件中, 并将网页中相应的url替换成本地url
    """

    def __init__(self, task):
        self.logger = logging.getLogger(LocalFilePipeline.__name__)
        self.task = task
        self.site = task.get_site()
        self.task_key = self.task.get_uuid()
        self.task_domain = task.get_site().domain
        self.lock = threading.Lock()

    def check_path(self, file_path):
        directory = os.path.dirname(file_path)
        with self.lock:
            if not os.path.exists(directory):
                os.makedirs(directory)
            elif not os.path.isdir(directory):
                self.logger.error("{} is a file, not directory".format(directory))

    def filter_query(self, page, url):
        """
        处理url中的参数，将参数当作url的路径来处理
        """
        url = tools.abs_url(page.url, url)
        if not url:
            return
        mu = tools.MutableUrl(url)
        if mu.query:
            li = mu.path.split('/')
            name = li[-1]
            name = tools.md5(mu.query) + name
            li[-1] = name
            mu.path = '/'.join(li)
            mu.query = ''
        li = mu.path.split('/')
        if not li[-1]:
            li[-1] = 'index.html'
        elif li[-1].find('.') == -1:
            li[-1] += '/index.html'
        mu.path = '/'.join(li)
        return mu.to_new_url()

    def to_local_url(self, parent_url, url):
        """
        将url转换为本地的url
        :param parent_url: 产生当前url的page
        :param url: url为包含域名的完整的URL
        """
        # 过滤掉其它域名的URL
        if not tools.has_same_host(self.task_domain, url):
            return
        # 网页中的路径转换成本地的路径
        # 找到公共前缀
        common_prefix = tools.common_path(parent_url, url)
        # 找到最近的路径前缀
        page_url_t = parent_url.replace(common_prefix, '').lstrip('/')
        depth = page_url_t.count('/')
        # 删除page_url中公共前缀，找到剩下的路径深度, 除了公共前缀的
        local_url = depth * '../' + url.replace(common_prefix, '').lstrip('/')
        if local_url.startswith('/'):
            local_url = '.' + local_url
        return local_url.replace('.//', './')

    def to_file_path(self, url):
        """
        将url转换为本地的文件路径，用于存储
        """
        # 删除fragment
        url = tools.delete_fragment(url)
        url = tools.delete_scheme(url)
        path = os.path.join(self.site.storage_path, url)
        return path

    def reconstruct_html(self, page):
        # 解析页面，替换其中所有的url
        page_query = PyQuery(page.raw_content)
        page_filter_url = self.filter_query(page, page.url)
        # 替换所有的href, src
        for tag in page_query('[href],[src]'):
            # 判断是否含有href, src
            tag = PyQuery(tag)
            attr_name = 'href'
            url = tag.attr(attr_name)
            if not url:
                attr_name = 'src'
                url = tag.attr(attr_name)
            # 过滤参数
            try:
                url = self.filter_query(page, url)
                if url:
                    url = self.to_local_url(page_filter_url, url)
                    tag.attr(attr_name, url)
            except Exception as e:
                self.logger.error('filter query error, url:' + url)
                raise e

        html = page_query.outer_html()
        try:
            raw_data = html.encode('utf-8')
        except UnicodeEncodeError as e:
            raw_data = html.encode(page.encoding)
        return raw_data

    def reconstruct_css(self, page):
        css_content = page.text
        page_filter_url = self.filter_query(page, page.url)
        for origin_url in r_url.findall(css_content):
            url = self.filter_query(page, origin_url)
            if url:
                url = self.to_local_url(page_filter_url, url)
                css_content = css_content.replace(origin_url, url)
        return css_content.encode(page.encoding)

    def reconstruct_data(self, page):
        """
        将page中的URL替换成本地对应的URL
        :type page: mirror.libs.components.Page
        """
        # 仅处理html页面中的URL
        if tools.is_html(page.content_type):
            return self.reconstruct_html(page)
        elif tools.is_css(page.content_type):
            return self.reconstruct_css(page)
        else:
            return page.raw_content

    def process(self, page):
        """
        将数据保存到本地
        :param page:
        :return:
        """
        # 存储文件路径
        file_query = self.filter_query(page, page.url)
        file_path = self.to_file_path(file_query)
        # 检测目录是否存在，不存在则创建新目录
        self.check_path(file_path)
        with open(file_path, 'wb') as fd:
            self.logger.error("write page, url: {}, file_path:{},  encoding: {}".format(page.url, file_path, page.encoding))
            fd.write(page.encoding.encode('utf-8') + b'\n\n' + page.raw_content)
            return
        # 获取原始数据, 如果是html页面则替换其中的url为本地的url
        raw_data = self.reconstruct_data(page)
        # 存储
        with open(file_path, 'wb') as fd:
            fd.write(raw_data)
            self.logger.info("storage a file, url:{}, file_path:{}".format(page.url, file_path))
