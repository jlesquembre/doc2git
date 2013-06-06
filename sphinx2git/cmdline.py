import subprocess
import os
import tempfile
import shutil
import shlex
import configparser
import sys
import sarge

DOCS = 'docs/source'
EXCLUDE = ['.buildinfo']
INI_FILE = 's2g.ini'

HEAD = 95
BLUE = 94
OK   = 92
WARN = 93
FAIL = 91
ENDC = '\033[0m'

def cprint(*text, color=HEAD):

    out = '{}'* len(text)
    out = out.format(*text)

    if color:
        code = '\033[{}m'.format(color)
        print (code, out, ENDC)
    else:
        print (out)


GITPATH = None

def get_git_path():
    wd = os.getcwd()

    while wd != '/':
        path = os.path.join(wd,'.git')
        if os.path.exists(path):
            return wd

        wd = os.path.split(wd)[0]

    cprint('!!!  Not a git repository', color=FAIL)
    sys.exit(0)


def main():

    global GITPATH
    GITPATH = get_git_path()

    conf = get_conf()

    if conf['git']['remote'] == '':
        remote_name = None
    else:
        remote_name = conf['git']['remote']

    remote = get_remote(conf['git']['service'], conf['git']['remote'])

    generate_output()


def get_conf():

    config_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   'config', INI_FILE)
    config = configparser.ConfigParser()
    config.read(config_filename)

    user_config_path = os.path.join(GITPATH, INI_FILE)

    if not os.path.exists(user_config_path):
        cprint('===  User configuration not found, using default values.')
        return config

    user_config = configparser.ConfigParser()
    user_config.read(user_config_path)

    cprint('===  User configuration found.')

    try:
        for section in user_config.sections():
            for key in user_config[section]:
                config[section][key] = user_config[section][key]
    except KeyError:
        cprint('###  Unknow option: ', key,' in section ', section, color=WARN )


    return config


'''def run(command, capture_out=True, show_err=False):

    output = subprocess.PIPE if capture_out else None
    err = subprocess.DEVNULL if capture_out else None

    with subprocess.Popen(shlex.split(command), stdout=output,
            stderr=err, universal_newlines=True) as proc:

        out = proc.stdout.read() if capture_out else ''
        ret = proc.poll()

    return out.strip(), ret'''

def check_exit_code(code):
    if code != 0:
        cprint('!!!  Last command fails, see previous output', color=FAIL)
        sys.exit(code)


def run(command, get_output=False, cwd=None):
    """By default, run all commands at GITPATH directory.
    If command fails, stop program execution.
    """
    if cwd is None:
        cwd = GITPATH

    cprint ('===')
    cprint ('===  Command: ', command)
    cprint ('===  CWD:     ', cwd)
    cprint ('===')

    if get_output:
        proc = sarge.capture_stdout(command, cwd=cwd)
        print (proc.stdout.decode(), end='')
        check_exit_code(proc.returncode)
        return proc.stdout.decode()
    else:
        proc = sarge.run(command, cwd=cwd)
        check_exit_code(proc.returncode)





def get_remote(service, remote_name):
    ret = run('git remote -v', get_output=True)
    #if ret != 0:
    #    raise Exception('Not a git repository!')

    # TODO remote is origin???
    for line in out.splitlines():
        if 'push' in line and service in line:
            if remote_name == '':
                return line.split()[1]
            elif line.split()[0] == remote_name:
                return line.split()[1]

    cprint('!!!  No remote url remote found, set one with "git remote add <name> <url>"', color=FAIL)
    sys.exit(0)


def push_to_gh_pages(remote, doc_path):
    run('git clone {} -b gh-pages tmp_repo'.format(remote), False)
    os.chdir('tmp_repo')
    out, ret = run('git show-ref --verify --quiet refs/heads/gh-pages')

    if ret != 0:  # gh-pages doesn't exists
        run('git checkout --orphan gh-pages')

    run('git rm -rf .')
    run('touch .nojekyll')
    for f in os.listdir(doc_path):
        if f not in EXCLUDE:
            shutil.move(os.path.join(doc_path,f), '.')

    run('git add -A', False)
    run('git commit -m "Autogenerated github-pages"', False)
    run('git push origin gh-pages', False)
Last command fails, see previous output
    os.chdir('..')


if __name__ == '__main__':
    main()

#if __name__ == '__main__':
def generate_output():
    #remote = get_remote()
    #cwd = os.getcwd()
    with tempfile.TemporaryDirectory(prefix='d2g_generated_doc') as tmp:

        shutil.copytree(GITPATH, os.path.join(tmp, 'copy'), ignore=shutil.ignore_patterns('.*'))

        doc_path = os.path.join(tmp, 'html')
        run('sphinx-build -W -b html -d {} {} {}', cwd=)
        #run('sphinx-build -W -b html -d {} {} {}'.
        #        format(os.path.join(tmp, 'doctrees'),
        #               os.path.join(tmp, 'copy', DOCS),
        #               doc_path), False)

        os.chdir(tmp)

        os.chdir(tmp)
        push_to_gh_pages(remote, doc_path)
