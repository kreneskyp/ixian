import subprocess


def execute(command, fail_silent=True):
    """Execute a shell command"""
    args = [arg for arg in command.split(' ') if arg]
    print(' '.join(args))
    code = subprocess.call(args)
    if not fail_silent and code:
        raise Exception('command returned non-zero code: %s' % code)


def format_args(*args):
    """format args for shell command"""
    return ' '.join(list(args))


def get_dev_uid():
    """get dev uid of running process"""
    return subprocess.check_output(['id', '-u'])[:-1]


def get_dev_gid():
    """get dev gid of running process"""
    return subprocess.check_output(['id', '-g'])[:-1]
