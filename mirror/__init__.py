# coding: utf-8
import os

from config.config import global_config
from mirror.libs.components import Site
from mirror.spider import Spider


def _set(site, name, value):
    if value:
        setattr(site, name, value)


def create_site():
    """
    :rtype: Site
    """
    site = Site()
    _set(site, 'domain', global_config.get('site::domain'))
    _set(site, 'thread_cnt', global_config.get_int('site::thread_cnt'))
    _set(site, 'user_agent', global_config.get('site::user_agent'))
    _set(site, 'default_cookies', global_config.get('site::default_cookies'))
    _set(site, 'charset', global_config.get('site::charset'))
    _set(site, 'sleep_time', global_config.get_int('site::sleep_time'))
    _set(site, 'time_out', global_config.get_int('site::time_out'))
    _set(site, 'retry_times', global_config.get_int('site::retry_times'))
    _set(site, 'retry_sleep_time', global_config.get_int('site::retry_sleep_time'))
    _set(site, 'storage_path', os.path.join(global_config.execute_dir, global_config.get('site::storage_path')))
    _set(site, 'key', global_config.get('site::key'))
    _set(site, 'start_urls', global_config.get('site::start_urls'))
    return site


def create_spider():
    site = create_site()
    return Spider(site)
