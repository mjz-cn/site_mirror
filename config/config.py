# coding: utf-8
import configparser
import os
import logging.config
import logging.handlers

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


# 初始化全局配置
def init_config():
    a = os.path.realpath(__file__)
    base_path = os.path.dirname(os.path.dirname(a))
    conf_path = os.path.join(base_path, 'conf.ini')
    return _Config(conf_path)


# 初始化logging
def init_log(log_path):
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-8.8s]  %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    file_handler = logging.handlers.TimedRotatingFileHandler(log_path)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)


global_config = init_config()

init_config(global_config.get("log::path"))
