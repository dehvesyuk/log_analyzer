import argparse
import os

import pytest

from helpers import is_log_and_report_date_equal
from log_analyzer import get_config, main, config, parse_config


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
    report_name = 'report-2017.06.30.html'
    cfg = get_config(
        local=config, file=parse_config(argparse.Namespace(config=None)))
    main(cfg)

    assert os.path.exists(os.path.join(config["report_dir"], report_name))
