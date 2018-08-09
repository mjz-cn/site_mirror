
-- 创建database
CREATE DATABASE IF NOT EXISTS mirror CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE mirror;


CREATE TABLE IF NOT EXISTS `t_url_duplicate_check` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `task_key` varchar(50) NOT NULL DEFAULT '',
  `url_md5` varchar(50) NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_task_url` (`task_key`,`url_md5`),
  KEY `idx_task` (`task_key`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;


CREATE TABLE IF NOT EXISTS `t_request_queue` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `task_key` varchar(50) NOT NULL DEFAULT '',
  `request_json` varchar(600) NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_task` (`task_key`),
  KEY `idx_time` (`create_time`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;