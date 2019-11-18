import os
import shutil

from power_shovel.utils import filesystem


def test_mkdir():
    path = "/tmp/mkdir_test/foo"
    if os.path.exists(path):
        shutil.rmtree(path)
    assert not os.path.exists(path)

    # test creating the directories
    filesystem.mkdir(path)
    assert os.path.exists(path)

    # calling it a second time should not raise an error
    filesystem.mkdir(path)
    assert os.path.exists(path)


def test_pwd():
    assert filesystem.pwd() == "/opt/power_shovel"
