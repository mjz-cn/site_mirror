# coding: utf-8

import hashlib
from urllib.parse import urlparse


def md5(s):
    m = hashlib.md5()
    if type(s) != bytes:
        s = str(s).encode('utf-8')
    m.update(s)
    return m.hexdigest()


def get_domain(url):
    if not url:
        return
    u = urlparse(url)
    return u.hostname


def has_same_domain(url1, url2):
    return get_domain(url1) == get_domain(url2)


def delete_fragment(url):
    return url
