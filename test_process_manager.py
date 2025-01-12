import asyncio
import time
from typing import NoReturn, Optional
from unittest import TestCase

from module.crawling_data.async_crawling_data import AsyncCrawlingData
from module.need_crawling_fund.get_fund_by_web import GetNeedCrawledFundByWeb4Test
from module.save_result.save_result_2_file import SaveResult2File
from process_manager import NeedCrawledFundModule, CrawlingDataModule, FundCrawlingResult, SaveResultModule, \
    TaskManager


class SimpleTestTaskManager(TestCase):
    """
    简单测试, 验证下整个链路是否符合预期, 有没有漏水的地方
    """

    class TestNeedCrawledFundModule(NeedCrawledFundModule):

        def init_generator(self):
            self.total = 100
            self.task_generator = (NeedCrawledFundModule.NeedCrawledOnceFund(str(i), str(i)) for i in range(self.total))

    class TestCrawlingDataModule(CrawlingDataModule):
        def __init__(self):
            self._result_list: list[FundCrawlingResult] = list()
            self._shutdown = False

        def shutdown(self):
            self._shutdown = True

        def do_crawling(self, task: NeedCrawledFundModule.NeedCrawledOnceFund):
            print("do_crawling")
            # 模拟从队列中取结果时的block
            while len(self._result_list) > 0:
                time.sleep(0.1)

            self._result_list.append(FundCrawlingResult(task.code, task.name))

        def has_next_result(self) -> bool:
            return not (self._shutdown and not self._result_list)

        def get_an_result(self) -> Optional[FundCrawlingResult]:
            print("get_an_result")
            # 模拟从队列中取结果时的block
            max_iter = 10
            while not self._result_list and max_iter > 0:
                max_iter -= 1
                time.sleep(0.1)

            result = self._result_list.pop()
            return result

    class TestSaveResultModule(SaveResultModule):

        def save_result(self, result: FundCrawlingResult) -> NoReturn:
            print(f'the result is {result.fund_info_dict}')

    def test_run(self):
        manager = TaskManager(SimpleTestTaskManager.TestNeedCrawledFundModule()
                              , SimpleTestTaskManager.TestCrawlingDataModule()
                              , SimpleTestTaskManager.TestSaveResultModule())
        asyncio.run(manager.run())


class SmokeTestTaskManager(TestCase):
    """
    冒烟测试, 小批量爬取基金信息, 主要用于验证数据的爬取和清洗逻辑
    """

    def test_run(self):
        GetNeedCrawledFundByWeb4Test.test_case_num = 100
        manager = TaskManager(GetNeedCrawledFundByWeb4Test()
                              , AsyncCrawlingData()
                              , SaveResult2File())
        manager.run()
