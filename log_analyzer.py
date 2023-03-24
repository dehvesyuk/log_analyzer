import os.path

from helpers import log_reader, parse_filename


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
    log_file = parse_filename(log_dir)


if __name__ == "__main__":
    main()
