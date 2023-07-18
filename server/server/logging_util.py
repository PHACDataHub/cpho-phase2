import getpass
import logging
import os
from abc import ABCMeta, abstractmethod

import requests
import structlog


def configure_logging(
    lowest_level_to_log="INFO",
    format_console_logs_as_json=True,
    slack_webhook_url=None,
    slack_webhook_fail_silent=False,
    mute_console=False,
):
    common_structlog_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        structlog.processors.UnicodeDecoder(),
    ]

    # There's a separate class of warnings (e.g. warning.warn) that, by default, are handled outside the logging system
    # (even though logging has its own WARNING category). They can be configured to surface as warning-level logs, which we want
    logging.captureWarnings(True)

    # Configure the standard library logging module, using structlog for formatting
    logging.config.dictConfig(
        get_logging_dict_config(
            common_structlog_processors,
            lowest_level_to_log,
            format_console_logs_as_json,
            slack_webhook_url,
            slack_webhook_fail_silent,
            mute_console,
        )
    )

    # From https://www.structlog.org/en/stable/standard-library.html#rendering-within-structlog
    # Effectively makes structlog a wrapper for the sandard library `logging` module, which makes
    # our above `logging` configuration the single source of truth (processors aside) on project logging, and means
    # `logging.getLogger()` and `structlog.get_logger()` produce consistent output (which is very nice to have when
    # packages might be logging via either)
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *common_structlog_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        # `wrapper_class` is the bound logger that you get back from
        # get_logger(). This one imitates the API of `logging.Logger`.
        wrapper_class=structlog.stdlib.BoundLogger,
        # `logger_factory` is used to create wrapped loggers that are used for
        # OUTPUT. This one returns a `logging.Logger`. The final value (a JSON
        # string) from the final processor (`JSONRenderer`) will be passed to
        # the method of the same name as that you've called on the bound logger.
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Effectively freeze configuration after creating the first bound
        # logger.
        cache_logger_on_first_use=True,
    )


def get_logging_dict_config(
    common_structlog_processors,
    lowest_level_to_log,
    format_console_logs_as_json,
    slack_webhook_url,
    slack_webhook_fail_silent,
    mute_console,
):
    console_handler_stream = (
        "ext://sys.stdout" if not mute_console else open(os.devnull, "w")
    )
    console_handler_formatter = (
        "json_formatter"
        if format_console_logs_as_json
        else "console_formatter"
    )

    slack_handler_fail_silent = (
        True if slack_webhook_url is None else slack_webhook_fail_silent
    )

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(),
                "foreign_pre_chain": common_structlog_processors,
            },
            "json_formatter": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": common_structlog_processors,
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
                "stream": console_handler_stream,
                "formatter": console_handler_formatter,
            },
            "slack": {
                "level": "ERROR",
                "class": "server.logging_util.SlackWebhookHandler",
                "url": slack_webhook_url,
                "fail_silent": slack_handler_fail_silent,
                "formatter": "plaintext_formatter",
            },
        },
        "root": {
            "level": lowest_level_to_log,
            "handlers": ["console", "slack"],
        },
    }


class AbstractJSONPostHandler(logging.Handler, metaclass=ABCMeta):
    def __init__(self, url, fail_silent):
        super().__init__()
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )

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
