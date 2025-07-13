import pytest
from src.utils.config import Config

def test_default_config_load():
    config = Config(config_path="nonexistent.yaml")
    assert config.telegram_bot_token == '' or isinstance(config.telegram_bot_token, str)
    assert isinstance(config.check_interval, int)
    assert isinstance(config.log_level, str)
