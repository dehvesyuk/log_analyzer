import os.path
import datetime
from typing import Dict, List, Tuple
from statistics import median
from string import Template
import json


from helpers import (
    get_last_log_filename, get_last_report_filename, get_log_dt,
    is_log_and_report_date_equal, log_reader, get_url_and_time_from_log, REPORT_TEMPLATE, REPORT_FILENAME_TEMPLATE
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


def prepare_data(data: Dict, total: int) -> List[Dict]:
    # TODO round all float params, add sort
    full_report = []
    total_req_time = count_total_req_time(data)
    for r in data.items():
        req_count = r[1]["count"]
        time_lst = r[1]["time"]
        time_sum = sum(time_lst)
        report = {
            "url": r[0],
            "count": req_count,
            "count_perc": req_count/total,
            "time_avg": average(time_lst),
            "time_max": max(time_lst),
            "time_med": median(time_lst),
            "time_perc": time_sum/total_req_time,
            "time_sum": time_sum
        }
        full_report.append(report)
    return full_report


def average(time_lst: List) -> float:
    return sum(time_lst) / len(time_lst)


def count_total_req_time(data: Dict) -> float:
    time_sum = sum([sum(r[1]["time"]) for r in data.items()])
    return round(time_sum, 3)


def parse_log(path: str) -> Tuple:
    data = {}
    total = 0
    for line in log_reader(path):
        total += 1
        url, time = get_url_and_time_from_log(line)
        if url and time:
            if url in data.keys():
                data[url]["time"].append(time)
                data[url]["count"] += 1
            else:
                data[url] = {}
                data[url]["count"] = 1
                data[url]["time"] = [time]
    return data, total


def render_report(data: List[Dict]) -> str:
    table_json = json.dumps(data, sort_keys=True)
    with open(REPORT_TEMPLATE) as tpl:
        template = Template(tpl.read())
        final_output = template.safe_substitute(table_json=table_json)
    return final_output


def save_report(final_output: str, report_dt: datetime, report_dir: str):
    dt_str = report_dt.strftime("%Y.%m.%d")
    report_filename = f"{report_dir}/{REPORT_FILENAME_TEMPLATE}{dt_str}.html"
    with open(report_filename, "w") as output:
        output.write(final_output)


def main():
    report_dir = config["REPORT_DIR"]
    log_dir = config["LOG_DIR"]
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    last_log = get_last_log_filename(log_dir)
    log_dt = get_log_dt(last_log)
    last_report = get_last_report_filename(report_dir)
    if is_log_and_report_date_equal(last_log, last_report):
        return

    full_path = f"{log_dir}/{last_log}"
    data, total = parse_log(full_path)
    report_data = prepare_data(data, total)
    report = render_report(report_data)
    save_report(report, log_dt, report_dir)


if __name__ == "__main__":
    main()
