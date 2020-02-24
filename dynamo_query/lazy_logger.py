import logging
from typing import Optional


class LazyLogger:
    log_level: int = logging.WARNING
    log_format: str = "%(name)s: %(levelname)-8s %(message)s"
    logger_name: str = "dynamoquery"
    _lazy_logger: Optional[logging.Logger]

    @property
    def _logger(self) -> logging.Logger:
        if self._lazy_logger is None:
            self._lazy_logger = self._get_default_logger()

        return self._lazy_logger

    def _get_default_logger(self) -> logging.Logger:
        logger = logging.getLogger(self.logger_name)
        if not logger.handlers:
            formatter = logging.Formatter(self.log_format)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            stream_handler.setLevel(self.log_level)
            logger.addHandler(stream_handler)
        logger.setLevel(self.log_level)
        return logger
