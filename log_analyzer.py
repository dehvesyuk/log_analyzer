import os.path

from helpers import get_last_log_filename, get_last_report_filename, is_log_and_report_date_equal, log_reader

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '  
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def main():
    report_dir = config["REPORT_DIR"]
    log_dir = config["LOG_DIR"]
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    last_log = get_last_log_filename(log_dir)
    last_report = get_last_report_filename(report_dir)
    if is_log_and_report_date_equal(last_log, last_report):
        return

    for line in log_reader(last_log):
        pass


if __name__ == "__main__":
    main()
