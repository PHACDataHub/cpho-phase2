import json
import logging
import os

import pytest
import responses
import structlog
from pytest import skip
from testfixtures import LogCapture

from server.logging_util import (
    AbstractJSONPostHandler,
    JSONLogFormatter,
    SlackWebhookHandler,
)


# found this pattern while looking around at handler libraries on GitHub,
# specifically from https://github.com/Mulanir/python-elasticsearch-logging/blob/main/tests/conftest.py
@pytest.fixture()
def logger_factory():
    loggers = (
        logging.getLogger("test_logger"),
        structlog.getLogger("test_structlogger"),
    )

    loggers_init_level = map(lambda logger: logger.level, loggers)
    loggers_init_handlers = map(lambda logger: logger.handlers, loggers)

    for logger in loggers:
        logger.setLevel(logging.DEBUG)

    def factory(handler=None):
        if handler:
            for logger in loggers:
                logger.addHandler(handler)

        return loggers

    yield factory

    for logger, init_level, init_handlers in zip(
        loggers, loggers_init_level, loggers_init_handlers
    ):
        logger.setLevel(init_level)

        logger.handlers.clear()
        for handler in init_handlers:
            logger.Handler(handler)


# IMPORTANT: while active, logCapture clobbers any existing logging configuration. This is reverted
# when it's `uninstall()` method is called, but that means it is only useful for testing config-agnostic
# things and properties
@pytest.fixture()
def log_capture():
    capture = LogCapture()
    yield capture
    capture.uninstall()


TEST_URL = "http://testing.notarealtld"


def test_json_logging_consistent_between_standard_logger_and_structlogger(
    logger_factory,
):
    # specifically want to test the project's logging configuration itself, so can't use log_capture (which
    # clobbers existing logging configuration). Need to do a bit of extra set up to capture log output,
    # using the logging configuration initialized in settings.py and, specifically, our JSONLogFormatter
    class CapturingHandler(logging.Handler):
        captured_logs = list()

        def emit(self, record):
            formatted = self.format(record)
            self.captured_logs.append(formatted)

    capturingHandler = CapturingHandler(level=logging.DEBUG)
    capturingHandler.setFormatter(JSONLogFormatter())
    test_logger, test_structlogger = logger_factory(capturingHandler)

    test_log_content = "Original error should be present in captured logs"

    test_logger.error(test_log_content)
    test_structlogger.error(test_log_content)

    captured_logs = capturingHandler.captured_logs
    assert len(captured_logs) == 2
    assert test_log_content in captured_logs[0]

    keys_to_ignore = ("logger", "lineno", "timestamp")

    def log_to_filtered_dict(json_string):
        return {
            k: v
            for k, v in json.loads(json_string).items()
            if k not in keys_to_ignore
        }

    assert log_to_filtered_dict(captured_logs[0]) == log_to_filtered_dict(
        captured_logs[1]
    )


# using the responses library is annoyingly surfacing the implementation detail that we currently use the requests library
# under the hood here, ugh. TODO Switch to httpretty, as a generic equivalent, once it has 3.10 support
@responses.activate
# short timeout as safety against a potential regression where the handler may try to handle it's _own_ exceptions/log calls, which would result in an ugly loop
@pytest.mark.timeout(3)
def test_json_post_handler_posts_json_containing_logged_text_to_provided_url(
    logger_factory, log_capture
):
    # can't test properties of AbstractJSONPostHandler directly, need to do so via an implementing class;
    # asserting this relationship as a pre-requisite
    assert issubclass(SlackWebhookHandler, AbstractJSONPostHandler)

    error_message = "just some arbitrary text to expect shows up somewhere in the POSTed JSON"

    def expected_request_matcher(request):
        is_json = request.headers["Content-Type"] == "application/json"
        contains_original_message = (
            not request.body.decode().find(error_message) == -1
        )

        if is_json and contains_original_message:
            return True, ""
        else:
            return (
                False,
                "Either not JSON or does not contain the original error log text",
            )

    # Will only catch calls that have JSON bodies that, somewhere, include the original error message text
    expected_endpoint = responses.post(
        TEST_URL,
        match=[expected_request_matcher],
        status=200,
    )

    # Will catch any calls that miss the expected endpoint, i.e. if the request doesn't have a JSON body containing the logged message
    unexpected_endpoint = responses.post(TEST_URL)

    handler = SlackWebhookHandler(url=TEST_URL, fail_silent=False)
    test_logger, _ = logger_factory(handler)
    test_logger.error(error_message)

    assert expected_endpoint.call_count == 1
    assert unexpected_endpoint.call_count == 0


@responses.activate
@pytest.mark.timeout(3)
def test_json_post_handler_logs_own_errors_without_trying_to_rehandle_them(
    logger_factory, log_capture
):
    assert issubclass(SlackWebhookHandler, AbstractJSONPostHandler)

    responses.post(TEST_URL, status=500)
    handler = SlackWebhookHandler(url=TEST_URL, fail_silent=False)

    test_logger, _ = logger_factory(handler)
    test_logger.error("Original error should be present in captured logs")
    log_capture.check_present(
        (
            test_logger.name,
            "ERROR",
            "Original error should be present in captured logs",
        )
    )

    # by convention, any logger belonging to server/logging_util.py should be prefixed by "server.logging_util",
    # so _not_ really relying on an implementation detail here... but brittle to the module renaming or the convention being broken
    assert (
        len(
            list(
                filter(
                    lambda record: not record.name.find("server.logging_util"),
                    log_capture.records,
                )
            )
        )
        > 0
    )


@responses.activate
@pytest.mark.timeout(3)
def test_json_post_handler_emits_no_error_logs_in_fail_silent_mode(
    logger_factory, log_capture
):
    assert issubclass(SlackWebhookHandler, AbstractJSONPostHandler)

    responses.post(TEST_URL, status=500)
    handler = SlackWebhookHandler(url=TEST_URL, fail_silent=True)

    test_logger, _ = logger_factory(handler)
    test_logger.error("Original error should be the only captured log")
    log_capture.check(
        (
            test_logger.name,
            "ERROR",
            "Original error should be the only captured log",
        )
    )
