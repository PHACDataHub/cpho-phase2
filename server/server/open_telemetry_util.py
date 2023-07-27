import logging
import os
import sys

import requests
import structlog
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.cloud_trace_propagator import (
    CloudTraceFormatPropagator,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

from server.config_util import get_project_config, is_running_tests

logger = logging.getLogger(__name__)


def instrument_app():
    config = get_project_config()
    IS_LOCAL_DEV = config("IS_LOCAL_DEV", cast=bool, default=False)
    DEV_TELEMETRY_CONSOLE_OUTPUT = config(
        "DEV_TELEMETRY_CONSOLE_OUTPUT", cast=bool, default=False
    )

    if is_running_tests():
        # TODO: maybe still instrument, just want to silence the output when the
        # test environment is detected
        return

    if IS_LOCAL_DEV:
        project_id = "local-dev"

        span_exporter = ConsoleSpanExporter(
            out=(
                sys.stdout
                if DEV_TELEMETRY_CONSOLE_OUTPUT
                else open(os.devnull, "w")
            )
        )
    else:
        project_id = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
        ).text

        span_exporter = CloudTraceSpanExporter(
            project_id=project_id,
        )

    # Propagate (or set) the X-Cloud-Trace-Context header
    set_global_textmap(CloudTraceFormatPropagator())

    # a BatchSpanProcessor is better for performance but uses a background process,
    # which would require tricky and careful management in Cloud Run. Even in the best case,
    # I expect the necessary tricks would still result in the occasional dropped trace.
    # BatchSpanProcessor also requires extra configuration when combined with gunicorn's process forking
    span_processor = SimpleSpanProcessor(span_exporter)

    tracer_provider = TracerProvider(active_span_processor=span_processor)

    logger.info("outter-test-log")

    def associate_request_logs_to_telemetry(span, request):
        logger.info("inner-test-log")
        logger.info(
            f"projects/{project_id}/traces/{trace.span.format_trace_id(span.get_span_context().trace_id)}",
        )
        logger.info(trace.span.format_span_id(span.get_span_context().span_id))
        structlog.contextvars.bind_contextvars(
            **{
                # see https://cloud.google.com/trace/docs/trace-log-integration#associating
                # and https://cloud.google.com/logging/docs/structured-logging#special-payload-fields
                "logging.googleapis.com/trace": f"projects/{project_id}/traces/{trace.span.format_trace_id(span.get_span_context().trace_id)}",
                "logging.googleapis.com/spanId": trace.span.format_span_id(
                    span.get_span_context().span_id
                ),
            }
        )

    DjangoInstrumentor().instrument(
        tracer_provider=tracer_provider,
        meter_provider=None,  # TODO
        request_hook=associate_request_logs_to_telemetry,
        is_sql_commentor_enabled=True,
    )
