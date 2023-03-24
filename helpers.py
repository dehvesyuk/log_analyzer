import gzip
import os


def log_reader(filename: str):
    name, ext = os.path.splitext(filename)
    open_method = gzip.open if ext == '.gz' else open
    with open_method(filename, 'rb') as line:
        yield line.readline()


def get_last_log_filename(log_dir: str):
    log_lst = os.listdir(log_dir)


def get_last_parsed_log_date() -> str:
    # в папке ./report найти дату последнего сформированного отчета
    pass
