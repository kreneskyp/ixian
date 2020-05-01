from ixian.config import CONFIG


def write_file(path, data):
    with open(path, "w") as file:
        file.write(data)
