# coding: utf-8
import configparser
import os
import logging.config
import logging.handlers

_SEPARATOR = "::"
_CONF_NAME = 'conf.ini'


def _parse(key):
    li = key.strip().split(_SEPARATOR)
    if len(li) != 2:
        logging.error('invalid config key ' + key)
    return li


class _Config:

    def __init__(self, conf_path, execute_dir):
        config = configparser.ConfigParser()
        config.read(conf_path, 'utf-8')

        self.conf_path = conf_path
        self.config = config
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

    def get(self, key):
        section, child_key = _parse(key)
        return self.config.get(section, child_key)


# 初始化全局配置
def init_config(execute_dir, conf_path=None):
    """
        配置文件查找顺序: 指定配置文件>执行目录下的配置文件>当前目录下的配置
    :return:
    """
    if not conf_path or not os.path.exists(conf_path):
        # 检测执行目录下是否有配置文件
        conf_path = os.path.join(execute_dir, 'config/' + _CONF_NAME)
    elif not os.path.exists(conf_path):
        py_path = os.path.realpath(__file__)
        conf_path = os.path.join(os.path.dirname(py_path), _CONF_NAME)
    return _Config(conf_path, execute_dir)


# 初始化logging
def init_log(log_path):
    log_path = os.path.join(global_config.execute_dir, log_path)
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-8.8s]  %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

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
