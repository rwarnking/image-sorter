import os
import unittest

from test_utils import TestUtils


class TestAll(unittest.TestCase):
    def test_run(self):
        TEST_DIR = os.path.dirname(os.path.abspath(__file__))

        test_num = "t1"
        t_u = TestUtils()
        t_u.sort(TEST_DIR, test_num)

        self.assertTrue(os.path.exists(TEST_DIR + "/2020"))
        # self.assertTrue(t_u.test_success(TEST_DIR, test_num))
