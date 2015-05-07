"""
Unit tests for modules in utils dir

If you run with nosetests -w unittest then $PWD=unittest
If you run with python unittest/test_utils.py then $PWD=PythiaPlotter
"""

import unittest
import sys
import os
import os.path
import shutil
from utils.requisite_checker import RequisiteChecker
from pprint import pprint
from utils.common import *


class Utils_Test(unittest.TestCase):
    """Test fns in common.py"""

    def test_check_file_exists(self):
        self.assertFalse(check_file_exists("./madeupFile.txt"))
        self.assertFalse(check_file_exists("../madeupFile.txt"))
        self.assertTrue(check_file_exists("./test_utils.py"))
        self.assertTrue(check_file_exists("../README.md"))

    def test_check_dir_exists(self):
        self.assertFalse(check_dir_exists("madeupdir"))
        self.assertFalse(check_dir_exists("../madeupdir"))
        self.assertTrue(check_dir_exists("../unittest"))

    def test_check_dir_exists_create(self):
        createDir = "testFakeDirCreate"
        if check_dir_exists(createDir):
            os.rmdir(createDir)
        check_dir_exists_create(createDir)
        self.assertTrue(check_dir_exists(createDir))
        os.rmdir(createDir)
        self.assertFalse(check_dir_exists(createDir))



class RequisiteChecker_Test(unittest.TestCase):
    """Test RequisiteChecker"""

    def setUp(self):
        self.real_prog = "vim"
        self.fake_prog = "fakeprog"
        self.real_mod = "argparse"
        self.fake_mod = "aaaaaaa"
        self.all_prog = [self.real_prog, self.fake_prog]
        self.all_mod = [self.real_mod, self.fake_mod]

        # Setup with 1 real program, 1 fake, 1 real module, 1 fake
        self.checkr = RequisiteChecker(programs=self.all_prog,
                                       modules=self.all_mod)
        # pprint(self.checkr.results)

    def test_real_program(self):
        self.assertTrue(self.checkr.results[self.real_prog])

    def test_fake_program(self):
        self.assertFalse(self.checkr.results[self.fake_prog])

    def test_real_module(self):
        self.assertTrue(self.checkr.results[self.real_mod])

    def test_fake_module(self):
        self.assertFalse(self.checkr.results[self.fake_mod])


def main():
    unittest.main()

if __name__ == '__main__':
    main()