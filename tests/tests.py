import tempfile
import os
import shutil
import sys
from io import StringIO
from configparser import ConfigParser
from subprocess import DEVNULL

from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    import mock

import sarge

from doc2git import cmdline
from doc2git.cmdline import (get_git_path, get_conf, run, get_remote, main,
                                generate_output, push_doc)


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

    def test_get_git_dir(self):
        os.makedirs('.git')
        self.assertEqual(get_git_path(), self.tempd)

    def test_no_git_dir(self):
        self.assertRaises(SystemExit, get_git_path)


class TestGetConf(TestCaseWithTmp):

    def test_get_default_conf(self):
        conf = get_conf()
        self.assertEqual(conf['git']['remote'], '')
        self.assertEqual(conf['git']['service'], 'github.com')

    def test_get_user_conf(self):
        with open('d2g.ini', 'a') as iniconf:
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
        self.assertRaises(SystemExit, run, 'false')


class TestGetGitRemote(TestCaseWithTmp):

    @classmethod
    def setUpClass(cls):
        cls.cmdout = '''origin  git@github.com:jlesquembre/doc2git.git (fetch)
                        origin  git@github.com:user/repo.git (push)
                        foo     git@github.com:foo/bar.git (push)'''

    def test_get_first_remote(self):
        with mock.patch('doc2git.cmdline.run') as runmock:
            runmock.return_value = self.cmdout
            self.assertEqual(get_remote('github'),
                             'git@github.com:user/repo.git')

    def test_get_remote_with_name(self):
        with mock.patch('doc2git.cmdline.run') as runmock:
            runmock.return_value = self.cmdout
            self.assertEqual(get_remote('github', 'foo'),
                             'git@github.com:foo/bar.git')

    def test_remote_no_exists(self):
        with mock.patch('doc2git.cmdline.run') as runmock:
            runmock.return_value = self.cmdout
            self.assertRaises(SystemExit, get_remote, 'bitbucket')


class TestGenerateOutput(TestCaseWithTmp):

    def test_generate_output(self):

        os.makedirs('.git')
        os.makedirs('test_dir')

        with tempfile.TemporaryDirectory(prefix='test') as tmp_test,\
                tempfile.TemporaryDirectory(prefix='d2g_') as tmp:

            generate_output(sarge.shell_format('cp -r test_dir {0}', tmp_test),
                            tmp)

            self.assertTrue(os.path.exists(os.path.join(tmp_test, 'test_dir')))
            self.assertFalse(os.path.exists(os.path.join(tmp_test, '.git')))


class TestMain(TestCaseWithTmp):

    @mock.patch('doc2git.cmdline.sarge_run')
    def test_main(self, m):
        m.side_effect = lambda *args, **kw: sarge.run(*args,
                                                      **dict(kw,
                                                             stdout=DEVNULL,
                                                             stderr=DEVNULL))
        # Create folders
        repo_dir = os.path.join(self.tempd, 'normal_repo')
        bare_dir = os.path.join(self.tempd, 'bare_repo')
        os.makedirs(repo_dir)
        os.makedirs(bare_dir)

        # Create git repo to simulate our real git repo
        sarge.run('touch readme', cwd=repo_dir, stdout=DEVNULL)
        sarge.run('git init', cwd=repo_dir, stdout=DEVNULL)
        sarge.run('git add .', cwd=repo_dir, stdout=DEVNULL)
        sarge.run('git commit -m "Test"', cwd=repo_dir, stdout=DEVNULL)

        # Create git repo to be used as remote
        sarge.run('git --bare init', cwd=bare_dir,
                  stdout=DEVNULL, stderr=DEVNULL)
        sarge.run('git remote add origin {}'.format(bare_dir), cwd=repo_dir,
                  stdout=DEVNULL, stderr=DEVNULL)
        sarge.run('git push origin master', cwd=repo_dir,
                  stdout=DEVNULL, stderr=DEVNULL)

        # Create ini file
        config = ConfigParser()
        config['doc'] = {'command': 'mkdir output && touch output/index.html'
                                    ' && touch output/foo.html',
                         'output_folder': 'output',
                         'exclude': 'foo.html',
                         'extra': 'bar.html'
                         }
        config['git'] = {'remote': '',
                         'service': 'bare_repo',
                         'branch': 'some_branch',
                         'message': 'Some message'
                         }
        with open(os.path.join(repo_dir, 'd2g.ini'), 'w') as configfile:
            config.write(configfile)

        os.chdir(repo_dir)
        main()

        files = sarge.get_stdout('git ls-tree --name-only -r {}'
                                 .format(config['git']['branch']),
                                 cwd=bare_dir)
        self.assertTrue('index.html' in files.split())
        self.assertTrue('bar.html' in files.split())
        self.assertTrue('foo.html' not in files.split())


class TestPushDoc(TestCaseWithTmp):
    @mock.patch('doc2git.cmdline.sarge_run')
    def test_push(self, m):

        m.side_effect = lambda *args, **kw: sarge.run(*args,
                                                      **dict(kw,
                                                             stdout=DEVNULL,
                                                             stderr=DEVNULL))

        repo_dir = os.path.join(self.tempd, 'normal_repo')
        bare_dir = os.path.join(self.tempd, 'bare_repo')

        os.makedirs(repo_dir)

        # Create git repo to be used as remote
        sarge.run('touch readme', cwd=repo_dir, stdout=DEVNULL)
        sarge.run('git init', cwd=repo_dir, stdout=DEVNULL)
        sarge.run('git add .', cwd=repo_dir, stdout=DEVNULL)
        sarge.run('git commit -m "Test"', cwd=repo_dir, stdout=DEVNULL)

        sarge.run('git clone --bare {} bare_repo'.format(repo_dir),
                  cwd=self.tempd, stdout=DEVNULL)
        # First push
        with tempfile.TemporaryDirectory(prefix='test') as tmp:

            output_dir = os.path.join(tmp, 'copy', 'output')
            os.makedirs(output_dir)
            sarge.run('touch output.txt', cwd=output_dir, stdout=DEVNULL)

            push_doc(bare_dir, 'dev', 'Commit msg', 'output', ['exclude'], '',
                     tmp)

            files = sarge.get_stdout('git ls-tree --name-only -r dev',
                                     cwd=bare_dir)
            self.assertTrue('output.txt' in files.split())

        # Push again ...
        with tempfile.TemporaryDirectory(prefix='test') as tmp:
            output_dir = os.path.join(tmp, 'copy', 'output')
            os.makedirs(output_dir)
            sarge.run('touch output_2.txt', cwd=output_dir, stdout=DEVNULL)

            push_doc(bare_dir, 'dev', 'New msg', 'output', ['exclude'], '',
                     tmp)

            out = sarge.get_stdout('git log dev -1 --pretty=format:%s',
                                   cwd=bare_dir)
            self.assertEqual(out, 'New msg')

            files = sarge.get_stdout('git ls-tree --name-only -r dev',
                                     cwd=bare_dir)
            self.assertTrue('output_2.txt' in files.split())
            self.assertFalse('output.txt' in files.split())
