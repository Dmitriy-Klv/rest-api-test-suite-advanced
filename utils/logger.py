import logging
import sys
import re
from logging import Logger, LogRecord
from typing import Any, Union
from utils.config import settings

class RecursiveMaskFilter(logging.Filter):
    SENSITIVE_FIELDS = {
        "email", "username", "password", "token", "accessToken",
        "refreshToken", "phone", "iban", "bic", "ssn", "birthday",
        "address", "zipcode", "street", "city"
    }

    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    TOKEN_PATTERN = re.compile(r'(?i)(bearer\s+|token\s+|password\s*[:=]\s*)[a-zA-Z0-9\._\-]+')

    def filter(self, record: LogRecord) -> bool:
        msg = record.msg
        if isinstance(msg, str):
            msg = self._mask_string(msg)
        elif isinstance(msg, (dict, list)):
            msg = self._mask_data(msg)
        record.msg = msg
        return True

    def _mask_string(self, text: str) -> str:
        text = self.EMAIL_PATTERN.sub("[MASKED_EMAIL]", text)
        text = self.TOKEN_PATTERN.sub(r'\1[MASKED_DATA]', text)
        return text

    def _mask_data(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                k: ("[MASKED_DATA]" if k.lower() in self.SENSITIVE_FIELDS else self._mask_data(v))
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._mask_data(item) for item in data]
        elif isinstance(data, str):
            return self._mask_string(data)
        return data

def get_logger(name: str) -> Logger:
    logger = logging.getLogger(name)
    logger.propagate = False

    if not logger.hasHandlers():
        logger.setLevel(settings.LOG_LEVEL.upper())

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(RecursiveMaskFilter())

        logger.addHandler(console_handler)

    return logger