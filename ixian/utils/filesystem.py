import os


def mkdir(path: str) -> None:
    """Make directories in path if they don't exist"""
    if not os.path.exists(path):
        os.makedirs(path)


def pwd() -> str:
    """Return working directory"""
    return os.getcwd()
