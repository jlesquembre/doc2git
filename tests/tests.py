from unittest import TestCase
import tempfile
import os

from nosetests import *

from sphinx2git import get_git_path

def test_get_git_path():

class TestGetGitPath(unittest):

    def setUp(self):
        self.originald = os.getcwd()
        self.tempd = tempfile.mkdtemp()
        os.chdir(self.tempd)
        os.makedirs('.git')

    def test_get_git_dir(self):
        self.assertEqual(get_git_dir(), os.path.join(self.tempd '.git'))

    def tearDown(self):
        os.chdir(self.originald)
        shutil.rmtree(self.tempd)






