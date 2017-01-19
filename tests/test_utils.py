"""
Unit tests for modules in utils dir

If you run with nosetests -w unittest then $PWD=unittest
If you run with python unittest/test_utils.py then $PWD=PythiaPlotter
"""


from __future__ import absolute_import
import unittest
import sys
import os
import os.path
import shutil
from pythiaplotter.utils.common import *


class Utils_Test(unittest.TestCase):
    """Test fns in common.py"""

    def test_check_file_exists(self):
        self.assertFalse(check_file_exists("./madeupFile.txt"))
        self.assertFalse(check_file_exists("../madeupFile.txt"))
        open("tempTestFile.txt", "a").close()
        self.assertTrue(check_file_exists("tempTestFile.txt"))
        os.remove("tempTestFile.txt")

    def test_check_dir_exists(self):
        self.assertFalse(check_dir_exists("madeupdir"))
        self.assertFalse(check_dir_exists("../madeupdir"))
        os.makedirs("tempTestDir")
        self.assertTrue((check_dir_exists("tempTestDir")))
        os.rmdir("tempTestDir")

    def test_check_dir_exists_create(self):
        """Tests check_dir_exists_create
        i.e. create dir it doens't already exist
        """
        createDir = "testFakeDirCreate"
        if check_dir_exists(createDir):
            os.rmdir(createDir)
        check_dir_exists_create(createDir)
        self.assertTrue(check_dir_exists(createDir))
        os.rmdir(createDir)
        self.assertFalse(check_dir_exists(createDir))


class RequisiteChecker_Test(unittest.TestCase):
    """Test requisite checker methods"""

    def test_real_program(self):
        self.assertTrue(check_program_exists("vim"))

    def test_fake_program(self):
        self.assertFalse(check_program_exists("fakeprog"))

    def test_real_module(self):
        self.assertTrue(check_module_exists("argparse"))

    def test_fake_module(self):
        self.assertFalse(check_module_exists("aaaaaaa"))


def main():
    unittest.main()

if __name__ == '__main__':
    main()