# coding: utf-8


class LocalFilePipeline:
    """
        将下载的内容保存到本地对应的文件中, 并将网页中相应的url替换成本地url
    """

    def __init__(self, task):
        self.task = task
        self.task_key = self.task.get_uuid()

    def process(self, page):
        pass
