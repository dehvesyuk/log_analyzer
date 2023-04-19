import os.path
import re

from helpers import (
    get_last_log_filename, get_last_report_filename, is_log_and_report_date_equal, log_reader, get_url_and_time_from_log
)

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '  
#                     '$request_time';
URL_TEMPLATE = '\[([^\]]+)\]'
TIME_TEMPLATE = '"([^"]+)"'


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


class Report:
    date = ''
    url = ''
    count = ''
    count_perc = ''
    time_avg = ''
    time_max = ''
    time_med = ''
    time_perc = ''
    time_sum = ''


def render_report(url: str, time: float):
    report = Report()
    return {}


def main():
    report_dir = config["REPORT_DIR"]
    log_dir = config["LOG_DIR"]
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    last_log = get_last_log_filename(log_dir)
    last_report = get_last_report_filename(report_dir)
    if is_log_and_report_date_equal(last_log, last_report):
        return

    reports = []
    full_path = f"{log_dir}/{last_log}"
    for line in log_reader(full_path):
        print(line)
        url, time = get_url_and_time_from_log(line)
        print(url, time)
        if url and time:
            reports.append(render_report(url, time))


if __name__ == "__main__":
    main()
