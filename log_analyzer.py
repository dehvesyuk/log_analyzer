import json
import os.path
from statistics import median
from string import Template
from typing import Tuple

from helpers import *

URL_TEMPLATE = '\[([^\]]+)\]'
TIME_TEMPLATE = '"([^"]+)"'


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "ERRORS_MAX_PERC": 10
}


def main():
    try:
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
        data, total, total_errors = parse_log(full_path)
        print('процент ошибок: ', round(total_errors/total*100, 2), '%')
        if total_errors/total*100 > config["ERRORS_MAX_PERC"]:
            # TODO add log (превышено допустимое число ошибок при парсинге, выполнение прервано)
            return
        report_data = prepare_data(data, total)
        report = render_report(report_data)
        save_report(report, log_dt, report_dir)
    except Exception as e:
        # TODO add log (неожиданная ошибка, выполнение прервано)
        pass


def prepare_data(data: Dict, total: int) -> List[Dict]:
    full_report = []
    total_req_time = count_total_req_time(data)
    for r in data.items():
        req_count = r[1]["count"]
        time_lst = r[1]["time"]
        time_sum = sum(time_lst)
        report = {
            "url": r[0],
            "count": req_count,
            "count_perc": round(req_count/total, 3),
            "time_avg": round(average(time_lst), 3),
            "time_max": max(time_lst),
            "time_med": round(median(time_lst), 3),
            "time_perc": round(time_sum/total_req_time, 3),
            "time_sum": round(time_sum, 3)
        }
        full_report.append(report)
    return sorted(full_report, key=lambda x: x["time_sum"], reverse=True)[:config["REPORT_SIZE"]]


def parse_log(path: str) -> Tuple[Dict, int, int]:
    data = {}
    total = 0
    total_errors = 0
    for line in log_reader(path):
        total += 1
        url, time = get_url_and_time_from_log(line)
        if not all((url, time)):
            total_errors += 1
        if url and time:
            if url in data.keys():
                data[url]["time"].append(time)
                data[url]["count"] += 1
            else:
                data[url] = {}
                data[url]["count"] = 1
                data[url]["time"] = [time]
    return data, total, total_errors


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


if __name__ == "__main__":
    main()
