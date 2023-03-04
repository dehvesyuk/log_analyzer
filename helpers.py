import gzip
import os


def log_reader(filename):
    name, ext = os.path.splitext(filename)
    open_method = open if ext == '.txt' else gzip.open
    with open_method(filename, 'rb') as line:
        yield line.readline()
