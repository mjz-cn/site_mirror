# coding: utf-8
import configparser
import os
import logging.config
import logging.handlers

import config.colorlog

_SEPARATOR = "::"
_CONF_NAME = 'conf.ini'


def _parse(key):
    li = key.strip().split(_SEPARATOR)
    if len(li) != 2:
        logging.error('invalid config key ' + key)
    return li


class _Config:

    def __init__(self, conf_path, execute_dir):
        _config = configparser.ConfigParser()
        _config.read(conf_path, 'utf-8')

        self.conf_path = conf_path
        self.config = _config
        self.execute_dir = execute_dir

    def get_int(self, key, default=0):
        val = self.get(key)
        if not val:
            return default
        return int(val)

    def get_bool(self, key, default=False):
        val = self.get(key)
        if not val:
            return default
        if val.lower() == 'false':
            return False
        return bool(val)

    def get_float(self, key, default=0.0):
        val = self.get(key)
        if not val:
            return default
        return float(val)

    def get_list(self, key, default=None, ty=str):
        if default is None:
            default = []
        val = self.get(key)
        if not val:
            return default
        return [ty(item.strip()) for item in val.split(',')]

    def get_tuple(self, key, default=None, ty=str):
        if default is None:
            default = []
        val = self.get(key)
        if not val:
            return default
        return (ty(item.strip()) for item in val.split(','))

    def get(self, key):
        section, child_key = _parse(key)
        val = self.config.get(section, child_key)
        if val:
            return val.strip()
        return val


# 初始化全局配置
def init_config(execute_dir, conf_path=None):
    """
        配置文件查找顺序: 指定配置文件>执行目录下的配置文件>当前目录下的配置
    :return:
    """
    if not conf_path or not conf_path.startswith('/'):
        # 检测执行目录下是否有配置文件
        if not conf_path:
            conf_path = _CONF_NAME
        conf_path_t = os.path.join(execute_dir, 'config/' + conf_path)
        # 检查代码路径下的配置文件
        if not os.path.exists(conf_path_t):
            py_path = os.path.realpath(__file__)
            conf_path_t = os.path.join(os.path.dirname(py_path), conf_path)
        conf_path = conf_path_t
    return _Config(conf_path, execute_dir)


# 初始化logging
def init_log(log_path):
    log_path = os.path.join(global_config.execute_dir, log_path)
    log_dir = os.path.dirname(log_path)
    log_level = global_config.get('log::level').upper()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.15s] [%(name)s] [%(levelname)-8.8s]  %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    file_handler = logging.handlers.TimedRotatingFileHandler(log_path)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)


global_config = None


def init(execute_dir, conf_path=None):
    global global_config
    global_config = init_config(execute_dir, conf_path)
    init_log(global_config.get("log::path"))
