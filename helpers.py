import gzip
import os
from datetime import datetime

LOG_FILENAME_TEMPLATE = "nginx-access-ui.log"
REPORT_FILENAME_TEMPLATE = "report-"


def log_reader(filename: str):
    name, ext = os.path.splitext(filename)
    open_method = gzip.open if ext == ".gz" else open
    with open_method(filename, "rb") as line:
        yield line.readline()


def get_last_log_filename(log_dir: str) -> str:
    dir_files = os.listdir(log_dir)
    log_list = [x for x in dir_files if LOG_FILENAME_TEMPLATE in x]
    log_list.sort(reverse=True, key=lambda x: x.split('.')[1])
    return log_list[0]


def get_last_report_filename(report_dir: str) -> str:
    dir_files = os.listdir(report_dir)
    report_list = [x for x in dir_files if REPORT_FILENAME_TEMPLATE in x]
    report_list.sort(reverse=True)
    return report_list[0]


def is_log_and_report_date_equal(log: str, report: str) -> bool:
    log_datetime = datetime.strptime(log.split('.')[1], "log-%Y%m%d")
    report_datetime = datetime.strptime(report, "report-%Y.%m.%d.html")
    return log_datetime == report_datetime
