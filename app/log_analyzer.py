import argparse
import configparser
import json
import logging
import os.path
from copy import deepcopy
from datetime import datetime
from statistics import median
from string import Template
from typing import Dict, List, Optional
from typing import Tuple

from helpers import (
    average, log_reader, get_log_dt, get_last_log_filename,
    get_last_report_filename, get_url_and_time_from_log, count_total_req_time,
    is_log_and_report_date_equal, REPORT_FILENAME_TEMPLATE, REPORT_TEMPLATE
)

URL_TEMPLATE = "\[([^\]]+)\]"  # noqa: W605
TIME_TEMPLATE = '"([^"]+)"'
DEFAULT_REPORT_BATCH_SIZE = 1000
DEFAULT_ERR_MAX_PERC = 10

config = {
    "report_size": DEFAULT_REPORT_BATCH_SIZE,
    "report_dir": "./reports",
    "log_dir": "./log",
    # "app_log_filename": "./app_log/log.log",
    "error_max_perc": DEFAULT_ERR_MAX_PERC
}

logging.basicConfig(
    level=logging.INFO,
    filename=config.get("app_log_filename"),
    filemode="w",
    format="[%(asctime)s] %(levelname).1s %(message)s",
    datefmt="'%Y.%m.%d% H:%M:%S"
)
# не нашел способа, как выбрать filename для logging ДО считывания конфига из
# файла (писать логи в файл или stdout) т.к. если обрабатывать конфиг при
# объявлении переменных то мы не сможем логировать ошибки парсинга конфига
# (а это требование из ТЗ)


def main(cfg: Dict):
    report_dir = cfg.get("report_dir")
    log_dir = cfg.get("log_dir")
    app_log_filename = cfg.get("app_log_filename")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    if app_log_filename:
        app_log_path = app_log_filename.rpartition('/')[0]
        if not os.path.exists(app_log_path):
            os.makedirs(app_log_path)

    last_log = get_last_log_filename(log_dir)
    log_dt = get_log_dt(last_log)
    last_report = get_last_report_filename(report_dir)
    if is_log_and_report_date_equal(last_log, last_report):
        logging.info(
            f"Файл с отчетом для даты {str(log_dt.date())} уже создан")
        return

    full_path = f"{log_dir}/{last_log}"
    data, total, total_error = parse_log(full_path)
    logging.info(f"current config: {cfg}")
    logging.info(f"Процент ошибок: {str(round(total_error/total*100, 2))}%")
    if total_error/total*100 > cfg.get("error_max_perc", DEFAULT_ERR_MAX_PERC):
        logging.error(
            "Превышено допустимое число ошибок при парсинге, "
            "выполнение прервано"
        )
        return

    report_data = prepare_data(data, total, cfg)
    report = render_report(report_data)
    save_report(report, log_dt, report_dir)
    logging.info("Файл с отчетом создан")


def prepare_data(data: Dict, total: int, cfg: Dict) -> List[Dict]:
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
    return sorted(
        full_report,
        key=lambda x: x["time_sum"],
        reverse=True
    )[:cfg.get("report_size", DEFAULT_REPORT_BATCH_SIZE)]


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


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    return parser.parse_args()


def get_config(local: Dict, file: Optional[Dict]) -> Dict:
    actual_config = deepcopy(local)
    if file:
        actual_config.update(**file)
    return actual_config


def parse_config(args) -> Optional[Dict]:
    file_config = configparser.ConfigParser()
    if args.config:
        try:
            file_config.read(args.config)
            file_config = dict(file_config.defaults())
            file_config["report_size"] = int(file_config["report_size"])
            file_config["error_max_perc"] = int(file_config["error_max_perc"])
            return file_config
        except KeyError:
            logging.error(
                "Файл конфигурации не существует либо его не удалось спарсить."
            )


if __name__ == "__main__":
    try:
        config = get_config(local=config, file=parse_config(get_args()))
        main(config)
    except Exception:
        logging.exception("Неожиданная ошибка, выполнение прервано")
