import pytest

from helpers import is_log_and_report_date_equal
from log_analyzer import get_config

"""
1. Нет файла лога (не ошибка)
2. Отчет уже создан (не ошибка)
3. Наличие конфига (выходим с ошибкой если конфига нет или не парсится)
4. Файл отчета успешно создан
5. Процент ошибок превышен
"""


def test_logfile_not_exists():
    pass

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
    config = get_config(local, file)
    assert config == expected_config


def test_make_report():
    pass
