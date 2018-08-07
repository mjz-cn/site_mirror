# coding: utf-8

import hashlib


def md5(s):
    m = hashlib.md5()
    t = type(s)
    if type(s) != bytes:
        s = str(s).encode('utf-8')
    m.update(s)
    return m.hexdigest()