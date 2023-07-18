import grp
import logging
import os
import pwd

import pytest
import responses
from pytest import skip
from testfixtures import LogCapture

from server.logging_util import AbstractJSONPostHandler, SlackWebhookHandler


# found this pattern while looking around at handler libraries on GitHub,
# specifically from https://github.com/Mulanir/python-elasticsearch-logging/blob/main/tests/conftest.py
@pytest.fixture(autouse=True)
def logger_factory():
    test_logger = logging.getLogger("test_logger")
    test_logger.setLevel(logging.DEBUG)

    def factory(handler):
        test_logger.addHandler(handler)

        return test_logger

    yield factory

    test_logger.handlers.clear()


@pytest.fixture(autouse=True)
def log_capture():
    capture = LogCapture()
    yield capture
    capture.uninstall()


TEST_URL = "http://testing.notarealtld"


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
    test_logger = logger_factory(handler)
    test_logger.error(error_message)

    assert expected_endpoint.call_count == 1
    assert unexpected_endpoint.call_count == 0


@responses.activate
# @pytest.mark.timeout(3)
def test_json_post_handler_logs_own_errors_without_trying_to_rehandle_them(
    logger_factory, log_capture
):
    assert issubclass(SlackWebhookHandler, AbstractJSONPostHandler)

    responses.post(TEST_URL, status=500)
    handler = SlackWebhookHandler(url=TEST_URL, fail_silent=False)

    test_logger = logger_factory(handler)
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

    test_logger = logger_factory(handler)
    test_logger.error("Original error should be the only captured log")
    log_capture.check(
        (
            test_logger.name,
            "ERROR",
            "Original error should be the only captured log",
        )
    )
