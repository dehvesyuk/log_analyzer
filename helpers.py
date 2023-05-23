import gzip
import os
import re
from datetime import datetime
from typing import Optional
from collections import namedtuple

LOG_FILENAME_TEMPLATE = "nginx-access-ui.log"
REPORT_TEMPLATE = "report_template.html"
REPORT_FILENAME_TEMPLATE = "report-"
REQUEST_TIME_PATTERN = "\d.\d{3}$"
REQUEST_URL_PATTERN = "\s/\S+\s"


def log_reader(filename: str):
    name, ext = os.path.splitext(filename)
    open_method = gzip.open if ext == ".gz" else open
    with open_method(filename, "rb") as f:
        for line in f:
            yield line.decode("utf-8")


def get_last_log_filename(log_dir: str) -> str:
    dir_files = os.listdir(log_dir)
    log_list = [x for x in dir_files if LOG_FILENAME_TEMPLATE in x]
    log_list.sort(reverse=True, key=lambda x: x.split('.')[1])
    return log_list[0]


def get_last_report_filename(report_dir: str) -> Optional[str]:
    dir_files = os.listdir(report_dir)
    report_list = [x for x in dir_files if REPORT_FILENAME_TEMPLATE in x]
    report_list.sort(reverse=True)
    return report_list[0] if report_list else None


def is_log_and_report_date_equal(log: str, report: Optional[str]) -> bool:
    if not report:
        return False
    log_datetime = get_log_dt(log)
    report_datetime = get_report_dt(report)
    return log_datetime == report_datetime


def get_log_dt(log: str) -> datetime:
    return datetime.strptime(log.split('.')[1], "log-%Y%m%d")


def get_report_dt(report: str) -> datetime:
    return datetime.strptime(report, "report-%Y.%m.%d.html")


def get_url_and_time_from_log(line: str) -> tuple:
    time_tmp = re.search(REQUEST_TIME_PATTERN, line)
    url_tmp = re.search(REQUEST_URL_PATTERN, line)
    if time_tmp and url_tmp:
        time = float(time_tmp.group())
        url = (url_tmp.group()).strip()
    else:
        print(line, "Ошибка данных")
        url, time = None, None
    return url, time
