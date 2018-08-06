# coding: utf-8
import configparser
import os

_SEPARATOR = "::"


def _parse(key):
    section, child_key = key.strip().split(_SEPARATOR)
    return section, child_key


class _Config:

    def __init__(self, conf_path):
        config = configparser.ConfigParser()
        config.read(conf_path)

        self.conf_path = conf_path
        self.config = config

    def get_int(self, key):
        section, child_key = _parse(key)
        return self.config.getint(section, child_key)

    def get_bool(self, key):
        section, child_key = _parse(key)
        return self.config.getboolean(section, child_key)

    def get_float(self, key):
        section, child_key = _parse(key)
        return self.config.getfloat(section, child_key)

    def get(self, key):
        section, child_key = _parse(key)
        return self.config.get(section, child_key)


def init_config():
    a = os.path.realpath(__file__)
    base_path = os.path.dirname(os.path.dirname(a))
    conf_path = os.path.join(base_path, 'conf.ini')
    return _Config(conf_path)


global_config = init_config()
