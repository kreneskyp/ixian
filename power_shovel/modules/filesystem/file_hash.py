import json
import hashlib
import os
from glob import glob
from itertools import chain
from stat import ST_MODE

from power_shovel.check.checker import MultiValueChecker, hash_object
from power_shovel.config import CONFIG


def get_flags(path):
    """Return permissions and flags in a format suitable for hashing"""
    return str(os.stat(path)[ST_MODE])


def hash_file(path):
    """
    Hash a single file including it's contents, permissions, and flags.

    :param path: path to file or directory
    :return: sha256 hash of path contents
    """
    hash = hashlib.sha256()
    hash.update(get_flags(path).encode('utf-8'))
    with open(path, 'rb', buffering=0) as f:
        for b in iter(lambda: f.read(128 * 1024), b''):
            hash.update(b)
    return hash.hexdigest()


def hash_dir(path):
    """ Hash the contents, permissions and flags of a directory. Subdirectories
    are recursed into and hashed.

    Filename's of contents are included in the hash. Renaming a file results in
    a different hash for the directory containing it.

    Only the relative path of contents is considered. Directories with
    identical contents and renamed directories will return the same hash.

    :param path: path of directory
    :return: sha256 hash of directory contents
    """
    content_hashes = {'___FLAGS___': get_flags(path)}
    contents = sorted(os.listdir(path))
    for child in contents:
        child_path = os.path.join(path, child)
        if os.path.isdir(child_path):
            content_hashes[child] = hash_dir(child_path)
        else:
            content_hashes[child] = hash_file(child_path)
    return hash_object(content_hashes)


def hash_path(path):
    """Hash file or directory

    :param path: path to hash
    :return: sha256 hash
    """
    if os.path.isdir(path):
        return hash_dir(path)
    else:
        return hash_file(path)


def hash_paths(*paths):
    """ hash directories and files
    :param paths: list of directories or file paths
    :return: dict mapping path to hash
    """
    return {path: hash_path(path) for path in paths}


class FileHash(MultiValueChecker):
    """Checker that hashes files and directories.

    Keys are paths that may include unix style wildcards and config variables.

    :Example:

    Checker(
       '/path/to/my/file',
       '/path/to/my/other/file',
       '/path/to/my/directory',
       '/wildcard/*'
    )

    Directory contents are recursively hashed.
    """

    @property
    def keys(self):
        """Returns paths, expanding any wildcards into matches."""
        _keys = super(FileHash, self).keys
        expanded = (glob(CONFIG.format(pattern)) for pattern in _keys)
        return list(chain(*expanded))

    def state(self):
        return hash_paths(*self.keys)
