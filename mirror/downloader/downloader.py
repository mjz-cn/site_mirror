# coding: utf-8
import logging

import requests
from requests import RequestException

from mirror.libs.components import Request

from mirror.libs.components import Page


class Downloader:

    def __init__(self, task):
        """
        :type task: mirror.spider.Spider
        """
        self.logger = logging.getLogger(Downloader.__name__)
        self.task = task
        self.site = self.task.get_site()
        self.task_key = self.task.get_uuid()

    def download(self, request):
        """
        :type request: mirror.libs.components.Request
        """
        url = request.url
        headers = self.site.headers
        try:
            resp = requests.get(url, headers=headers)
        except RequestException as e:
            self.logger.warning("download page error, url:{}, exception: {}".format(url, e))
            return self.cycle_retry(request)

        status_code = resp.status_code
        request.put_extra(Request.STATUS_CODE, status_code)
        page = Page(request, resp)

        if self.site.accept(page):
            return page
        else:
            logging.warning(
                "reject page, status_code: {}, content_type: {}, url: {}".format(status_code, page.content_type, url))
            return None

    def cycle_retry(self, request):
        retry_times = request.get_extra(Request.CYCLE_TRIED_TIMES)
        if retry_times is None:
            retry_times = 0

        if retry_times > self.site.retry_times:
            page = Page(request)
            retry_times += 1
            request.put_extra(Request.CYCLE_TRIED_TIMES, retry_times)
            page.add_target_request(request)
            return page

        return None
