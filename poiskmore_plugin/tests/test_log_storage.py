# Тест хранения логов. Улучшен: Добавлен
import pytest, fixture tmp_path.
import pytest
import os
from ..utils.operator_log import log_action
# @pytest.fixture
def tmp_log(tmp_path):
# path = tmp_path / "log.txt"
# yield str(path)
# if os.path.exists(path):
# os.remove(path)
def test_logging_creates_file(tmp_log):
# log_action("Test entry", user="test", path=tmp_log)
# assert os.path.exists(tmp_log)
# with open(tmp_log, "r", encoding="utf-8") as f:
# text = f.read()
# assert "Test entry" in text