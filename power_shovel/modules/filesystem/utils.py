import os
import subprocess


def mkdir(path):
    """Make directories in path if they don't exist"""
    if not os.path.exists(path):
        os.makedirs(path)


def pwd():
    """Return working directory"""
    return os.getcwd()


def touch(path):
    """Unix touch command"""
    subprocess.Popen(['touch', path])
