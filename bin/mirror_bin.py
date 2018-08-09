# coding: utf-8
import os
import sys
import argparse

a = os.path.realpath(__file__)
base_path = os.path.dirname(os.path.dirname(a))


def main():
    ap = argparse.ArgumentParser(description='future')
    ap.add_argument('-d', '--executeDir', type=str,
                    help='执行目录，日志，网站会存在这个目录下面',
                    default=base_path)
    ap.add_argument('-c', '--confPath', type=str,
                    help='配置文件路径, 配置文件查找顺序: 指定配置文件>执行目录下的配置文件>当前目录下的配置',
                    default=None)
    args = ap.parse_args()
    sys.path.append(base_path)

    # 添加配置文件
    from config import config
    config.init(args.executeDir, args.confPath)
    import mirror
    s = mirror.create_spider()
    s.run()


if __name__ == '__main__':
    main()
