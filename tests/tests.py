import tempfile
import os
import shutil
from io import StringIO
import sys

from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    import mock

from sarge import shell_format

#from nosetests import *
from sphinx2git import cmdline
from sphinx2git.cmdline import (get_git_path, get_conf, run, get_remote,
                                check_exit_code, generate_output, push_doc)

class TestCaseWithTmp(TestCase):

    def setUp(self):
        self.originald = os.getcwd()
        self.tempd = tempfile.mkdtemp()
        os.chdir(self.tempd)
        cmdline.GITPATH = self.tempd

    def tearDown(self):
        os.chdir(self.originald)
        shutil.rmtree(self.tempd)

class TestGetGitPath(TestCaseWithTmp):

    #def setUp(self):

        #self.old_stdout = sys.stdout
        #sys.stdout = self.stdout = StringIO()

    def test_get_git_dir(self):
        os.makedirs('.git')
        self.assertEqual(get_git_path(), self.tempd)

    def test_no_git_dir(self):
        self.assertRaises(SystemExit, get_git_path)

    #def tearDown(self):

        #sys.stdout = self.old_stdout



class TestGetConf(TestCaseWithTmp):

    def test_get_default_conf(self):
        conf = get_conf()
        self.assertEqual(conf['git']['remote'], '')
        self.assertEqual(conf['git']['service'], 'github.com')

    def test_get_user_conf(self):
        with open('s2g.ini', 'a') as iniconf:
            iniconf.write('[git]\n')
            iniconf.write('remote = foo\n')
            iniconf.write('service = bar\n')
            iniconf.write('foo = foo\n')

            iniconf.write('[bar]\n')
            iniconf.write('foo = foo\n')

        conf = get_conf()
        self.assertEqual(conf['git']['remote'], 'foo')
        self.assertEqual(conf['git']['service'], 'bar')
        self.assertEqual(conf['git']['branch'], 'gh-pages')

        self.assertTrue('git' in conf)
        self.assertFalse('foo' in conf)

        self.assertFalse('foo' in conf['git'])


class TestRun(TestCaseWithTmp):

    def test_run(self):
        self.assertEqual(self.tempd, run('pwd', True).strip())

    def test_run_other_wd(self):
        self.assertEqual(tempfile.gettempdir(),
                         run('pwd', True, cwd=tempfile.gettempdir()).strip())


    def test_run_no_capture(self):
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        run('pwd', True)

        out = mystdout.getvalue().split('\n')[-2]
        sys.stdout = old_stdout


        self.assertEqual(self.tempd, out)

    def test_invalid_command(self):
        self.assertRaises(SystemExit, run, 'false' )


class TestGetGitRemote(TestCaseWithTmp):

    @classmethod
    def setUpClass(cls):
        cls.cmdout = '''origin  git@github.com:jlesquembre/sphinx2git.git (fetch)
                        origin  git@github.com:user/repo.git (push)
                        foo     git@github.com:foo/bar.git (push)'''

    def test_get_first_remote(self):
        with mock.patch('sphinx2git.cmdline.run') as runmock:
            runmock.return_value = self.cmdout
            self.assertEqual(get_remote('github'), 'git@github.com:user/repo.git')


    def test_get_remote_with_name(self):
        with mock.patch('sphinx2git.cmdline.run') as runmock:
            runmock.return_value = self.cmdout
            self.assertEqual(get_remote('github', 'foo'), 'git@github.com:foo/bar.git')


    def test_remote_no_exists(self):
        with mock.patch('sphinx2git.cmdline.run') as runmock:
            runmock.return_value = self.cmdout
            self.assertRaises(SystemExit, get_remote, 'bitbucket')

class TestGenerateOutput(TestCaseWithTmp):

    def test_generate_output(self):

        os.makedirs('.git')
        os.makedirs('test_dir')

        with tempfile.TemporaryDirectory(prefix='test') as tmp_test,\
                tempfile.TemporaryDirectory(prefix='d2g_') as tmp:

            generate_output(shell_format('cp -r test_dir {0}', tmp_test), tmp)

            self.assertTrue(os.path.exists(os.path.join(tmp_test, 'test_dir')))
            self.assertFalse(os.path.exists(os.path.join(tmp_test, '.git')))



class TestPushDoc(TestCaseWithTmp):

    def test_push(self):
        # Create git repo to be used as remote
        sarge.run('touch readme', cwd=self.tempd)
        sarge.run('git init', cwd=self.tempd)
        sarge.run('git add .', cwd=self.tempd)
        sarge.run('git commit -m "Test"', cwd=self.tempd)

        with tempfile.TemporaryDirectory(prefix='test') as tmp:
            output_dir = os.path.join(tmp, 'copy', 'output')
            os.makedirs(output_dir)
            sarge.run('touch output.txt', cwd=output_dir)

            push_doc(self.tempd, 'dev', 'output', ['exclude'], '', tmp)

            command = sarge.run('git checkout dev', cwd=self.tempd)
            self.assertEqual(command.returncode, 0)
