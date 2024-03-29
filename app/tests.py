import argparse
import os
import pytest
import gzip

from helpers import is_log_and_report_date_equal
from log_analyzer import get_config, main, config, parse_config

LOG_DATA = b'1.196.116.32 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/' \
           b'banner/25019354 HTTP/1.1" 200 927 "-" "Lynx/2.8.8dev.9 libwww-' \
           b'FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-2190034393' \
           b'-4708-9752759" "dc7161be3" 0.390\n' \
           b'1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300] "GET' \
           b' /api/1/photogenic_banners/list/?server_name=WIN7RB4 HTTP/1.1"' \
           b' 200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708' \
           b'-9752770" "-" 0.133\n' \
           b'1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/' \
           b'banner/16852664 HTTP/1.1" 200 19415 "-" "Slotovod" "-" "' \
           b'1498697422-2118016444-4708-9752769" "712e90144abee9" 0.199\n' \
           b'1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot/' \
           b'4705/groups HTTP/1.1" 200 2613 "-" "Lynx/2.8.8dev.9 libwww-FM/' \
           b'2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057' \
           b'-4708-9752745" "2a828197ae235b0b3cb" 0.704\n' \
           b'1.168.65.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/' \
           b'internal/banner/24294027/info HTTP/1.1" 200 407 "-" "-" "-" "' \
           b'1498697422-2539198130-4709-9928846" "89f7f1be37d" 0.146\n' \
           b'1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/' \
           b'group/1769230/banners HTTP/1.1" 200 1020 "-" "Configovod" "-"' \
           b' "1498697422-2118016444-4708-9752747" "712e90144abee9" 0.628\n' \
           b'1.194.135.240 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/' \
           b'group/7786679/statistic/sites/?date_type=day&date_from=2017-06' \
           b'-28&date_to=2017-06-28 HTTP/1.1" 200 22 "-" "python-requests/' \
           b'2.13.0" "-" "1498697422-3979856266-4708-9752772" "' \
           b'8a7741a54297568b" 0.067\n' \
           b'1.169.137.128 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/' \
           b'banner/1717161 HTTP/1.1" 200 2116 "-" "Slotovod" "-" "' \
           b'1498697422-2118016444-4708-9752771" "712e90144abee9" 0.138\n' \
           b'1.166.85.48 -  - [29/Jun/2017:03:50:22 +0300] "GET /export/' \
           b'appinstall_raw/2017-06-29/ HTTP/1.0" 200 28358 "-" ' \
           b'"Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.0.12)' \
           b' Gecko/2009070611 Firefox/3.0.12 (.NET CLR 3.5.30729)" ' \
           b'"-" "-" "-" 0.003\n' \
           b'1.199.4.96 -  - [29/Jun/2017:03:50:22 +0300] "GET /api/v2/slot' \
           b'/4822/groups HTTP/1.1" 200 22 "-" "Lynx/2.8.8dev.9 libwww-FM/' \
           b'2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498697422-3800516057-' \
           b'4708-9752773" "2a828197ae235b0b3cb" 0.157\n'


@pytest.mark.parametrize("log_path, report_path, expected_result", [  # noqa
    ("nginx-access-ui.log-20170630.gz", "report-2017.06.30.html", True),
    ("nginx-access-ui.log-20170630.gz", "", False),
    ("", "", False)
])
def test_report_already_exists(log_path, report_path, expected_result):
    result = is_log_and_report_date_equal(log_path, report_path)

    assert result == expected_result

@pytest.mark.parametrize("local, file, expected_config", [  # noqa
    ({"test": "test_local"}, {"test": "test_file"}, {"test": "test_file"}),
    ({"test": "test_local"}, {}, {"test": "test_local"}),
])
def test_config(local, file, expected_config):
    cfg = get_config(local, file)

    assert cfg == expected_config


def test_create_report():
    report_name = 'report-2018.06.30.html'
    log_name = 'nginx-access-ui.log-20180630.gz'
    if "log" not in os.listdir("app"):
        os.mkdir("app/log")

    with gzip.open(f"app/log/{log_name}", "wb") as f:
        f.write(LOG_DATA)

    cfg = get_config(
        local=config, file=parse_config(argparse.Namespace(config=None)))
    main(cfg)

    assert os.path.exists(os.path.join(config["report_dir"], report_name))
