import getpass
import os
from abc import ABCMeta, abstractmethod
from logging import Handler, getLogger

import requests
import structlog
from decouple import config

structlog_pre_chain = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
]


def get_logging_dict_config(
    lowest_level_to_log=config("LOWEST_LOG_LEVEL", "INFO"),
    format_console_logs_as_json=config("FORMAT_CONSOLE_LOGS_AS_JSON", True),
    slack_webhook_url=config("SLACK_WEBHOOK_URL", None),
    slack_webhook_fail_silent=config(
        "SLACK_WEBHOOK_FAIL_SILENT",
        # default to failing silent if webhook URL not set, failing loud otherwise
        bool(config("SLACK_WEBHOOK_URL", None)),
    ),
    mute_console=False,
):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "flat_console_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(),
                "foreign_pre_chain": structlog_pre_chain,
            },
            "json_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": structlog_pre_chain,
            },
            "plaintext_formatter": {
                "format": "[%(asctime)s] %(levelname)s [%(name)s:%(module)s:%(lineno)s] %(message)s",
                "datefmt": "%d/%b/%Y %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout"
                if not mute_console
                else open(os.devnull, "w"),
                "formatter": "json_formatter"
                if format_console_logs_as_json
                else "console_formatter",
            },
            "slack": {
                "level": "ERROR",
                "class": "server.logging_utils.SlackWebhookHandler",
                "url": slack_webhook_url,
                "fail_silent": slack_webhook_fail_silent,
                "formatter": "plaintext_formatter",
            },
        },
        "root": {
            "level": lowest_level_to_log,
            "handlers": ["console", "slack"],
        },
    }


class AbstractJSONPostHandler(Handler, metaclass=ABCMeta):
    def __init__(self, url, fail_silent):
        super().__init__()
        self.logger = getLogger(f"{__name__}.{self.__class__.__name__}")

        self.url = url
        self.fail_silent = fail_silent

    def emit(self, record):
        is_own_error_log = record.name == self.logger.name and (
            record.levelname == "ERROR" or record.levelname == "CRITICAL"
        )

        if not is_own_error_log:
            try:
                response = requests.post(
                    self.url,
                    json=self.get_json_from_record(record),
                    timeout=1,
                )

                response.raise_for_status()

            except requests.RequestException as exception:
                if not self.fail_silent:
                    self.logger.error(
                        '%s\'s logging request to URL "%s" failed',
                        self.__class__.__name__,
                        self.url,
                        exc_info=exception,
                    )

    @abstractmethod
    def get_json_from_record(self, record):
        pass


class SlackWebhookHandler(AbstractJSONPostHandler):
    def get_json_from_record(self, record):
        return {"text": self.format(record)}
