import os


def file_names(path):
    f = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        f.append(filenames)
    return f
