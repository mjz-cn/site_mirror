# coding: utf-8
import logging
import os


class LocalFilePipeline:
    """
        将下载的内容保存到本地对应的文件中, 并将网页中相应的url替换成本地url
    """

    def __init__(self, task):
        self.logger = logging.getLogger(LocalFilePipeline.__name__)
        self.task = task
        self.task_key = self.task.get_uuid()

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
        path = self.downpath
        dires[len(dires) - 1] = self.pfx2localpfx(dires[len(dires) - 1])
        for dire in dires:
            path = os.path.join(path, dire)
        return path

    def to_local_url(self, url):
        """
        将url转换为本地的url
        :param url:
        :return:
        """
        if '://' in url:
            if 'google.' in url:
                return '#'
            elif url.startswith(self.siteurl):
                url = url.replace(self.siteurl, '')
                cnt = self.parenturl.count('/') - 3
                for i in range(cnt):
                    url = '../' + url
        if url.startswith('/'):
            url = '.' + url
        if url.endswith('/'):
            return url
        pos = url.rfind('/')
        postfix = self.pfx2localpfx(url[pos + 1:])
        return url[:pos + 1] + postfix

    def reconstruct_data(self, page):
        """
        将page中的URL替换成本地对应的URL
        """
        return page.raw_content

    def process(self, page):
        """
        将数据保存到本地
        :param page:
        :return:
        """
        file_path = self.to_file_path(page.url)
        raw_data = self.reconstruct_data(page)
        with open(file_path, 'wb') as fd:
            fd.write(raw_data)
            self.logger.info("storage a file, url:{}, file_path:{}".format(page.url, file_path))
