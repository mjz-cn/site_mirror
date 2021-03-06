# coding: utf-8

import hashlib
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib import parse

from atomos import atomic

from config import config


def _raise_thread_exception(future):
    if future._exception:
        raise future._exception


class CountableThreadPool:

    def __init__(self, thread_cnt, thread_prefix):
        if not thread_cnt:
            thread_cnt = (os.cpu_count() or 1) * 5
        self.thread_cnt = thread_cnt
        self._thread_alive = atomic.AtomicInteger()
        self._thread_pool = ThreadPoolExecutor(thread_cnt, thread_prefix)

        self._reentrant_lock = threading.RLock()
        self._condition = threading.Condition(self._reentrant_lock)

    def submit(self, runner):
        # 一次只执行固定数量的线程，如果超过则等待
        if self._thread_alive.get() >= self.thread_cnt:
            with self._reentrant_lock:
                while self._thread_alive.get() >= self.thread_cnt:
                    self._condition.wait()
        self._thread_alive.get_and_add(1)

        def runner_wrapper():
            try:
                runner()
            finally:
                with self._reentrant_lock:
                    self._thread_alive.get_and_subtract(1)
                    self._condition.notify()

        future = self._thread_pool.submit(runner_wrapper)
        future.add_done_callback(_raise_thread_exception)

    def get_thread_alive(self):
        return self._thread_alive.get()

    def shut_down(self):
        self._thread_pool.shutdown()


class MutableUrl:
    """
    对url的封装，使其容易修改
    """

    def __init__(self, url):
        self.origin_url = url
        parse_result = parse.urlparse(url)

        self.scheme = parse_result.scheme
        self.netloc = parse_result.netloc
        self.path = parse_result.path
        self.params = parse_result.params
        self.query = parse_result.query
        self.fragment = parse_result.fragment
        self.parse_result = parse_result

    def to_parse_result(self):
        return parse.ParseResult(self.scheme, self.netloc, self.path, self.params, self.query, self.fragment)

    def to_new_url(self):
        return parse.urlunparse(self.to_parse_result())


def md5(s):
    m = hashlib.md5()
    if type(s) != bytes:
        s = str(s).encode('utf-8')
    m.update(s)
    return m.hexdigest()


def get_host(url):
    if not url:
        return
    u = parse.urlparse(url)
    return u.hostname


def has_same_host(url1, url2):
    return get_host(url1) == get_host(url2)


def delete_fragment(url):
    return parse.urldefrag(url).url


def delete_scheme(url):
    mu = MutableUrl(url)
    mu.scheme = ''
    return mu.to_new_url().lstrip('/')


def abs_url(refer, url):
    # 过滤掉无效的URL
    if url:
        url = url.strip()
    if not url or url.startswith('#') or url.startswith('javascript:') or url.startswith('mailto:'):
        return
    up = parse.urlparse(refer)
    if url.startswith('//'):
        return up.scheme + ':' + url
    return parse.urljoin(refer, url)


def is_html(content_type):
    return 'text/html' == content_type


def is_css(content_type):
    return 'text/css' == content_type


def should_process(content_type):
    return content_type in ['text/html', 'text/css']


def common_path(url1, url2):
    li = os.path.commonprefix([url1.split('/'), url2.split('/')])
    return '/'.join(li)


def replace_suffix(url):
    mu = MutableUrl(url)
    url_path = mu.path
    li = url_path.split('/')
    if li[-1]:
        suffix_li = li[-1].split('.')
        if len(suffix_li) >= 2:
            suffix = suffix_li[-1]
            if suffix in config.global_config.get_tuple('params::to_html'):
                suffix = 'html'
                suffix_li[-1] = suffix
                li[-1] = '.'.join(suffix_li)
                url_path = '/'.join(li)
                mu.path = url_path
                return mu.to_new_url()
    return url
