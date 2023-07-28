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
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

from server.config_util import get_project_config, is_running_tests
from server.logging_util import add_metadata_to_all_logs_for_current_request


def instrument_app():
    config = get_project_config()
    IS_LOCAL_DEV = config("IS_LOCAL_DEV", cast=bool, default=False)
    DEV_TELEMETRY_CONSOLE_OUTPUT = config(
        "DEV_TELEMETRY_CONSOLE_OUTPUT", cast=bool, default=False
    )

    if IS_LOCAL_DEV:
        project_id = "local-dev"

        span_exporter = ConsoleSpanExporter(
            out=(
                sys.stdout
                if DEV_TELEMETRY_CONSOLE_OUTPUT and not is_running_tests()
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

    # Propagate the X-Cloud-Trace-Context header if present. Adds it otherwise
    set_global_textmap(CloudTraceFormatPropagator())

    # A BatchSpanProcessor is better for performance but uses a background process,
    # which would require tricky and careful management in Cloud Run. Even in the best case,
    # I expect the necessary tricks would still result in the occasional dropped trace.
    # BatchSpanProcessor also requires extra configuration when combined with gunicorn's process forking
    span_processor = SimpleSpanProcessor(span_exporter)

    tracer_provider = TracerProvider(
        active_span_processor=span_processor,
        # Always sample, even if propagating a trace that wasn't sampled in earlier stages (load balancer, etc).
        # This could be too noisy on a busier app, but should be fine for CPHO's expected usage
        sampler=sampling.ALWAYS_ON,
    )

    def associate_request_logs_to_telemetry(span, request):
        add_metadata_to_all_logs_for_current_request(
            {
                # see https://cloud.google.com/trace/docs/trace-log-integration#associating
                # and https://cloud.google.com/logging/docs/structured-logging#special-payload-fields
                "logging.googleapis.com/trace": (
                    f"projects/{project_id}/traces/{trace.span.format_trace_id(span.get_span_context().trace_id)}"
                ),
                "logging.googleapis.com/spanId": (
                    trace.span.format_span_id(span.get_span_context().span_id)
                ),
                # This one's awkward, see: https://www.w3.org/TR/trace-context/#sampled-flag
                # Right now the only trace flag is the "sampled flag", so `trace_flags` is either 0 or 1;
                # the "correct" way to get `trace_sampled` would be `span.get_span_context().trace_flags == 1`,
                # but that seems fragile and might not pick up on overrides, like sampler=sampling.ALWAYS_ON?
                # `span.is_recording()` doesn't indicate that the _whole_ trace is sampled, but it should
                # indicate that the current span within the trace is reporting/being sampled, which is what this
                # log field is actually intended for
                "logging.googleapis.com/trace_sampled": span.is_recording(),
            }
        )

    DjangoInstrumentor().instrument(
        tracer_provider=tracer_provider,
        meter_provider=None,  # TODO
        request_hook=associate_request_logs_to_telemetry,
        is_sql_commentor_enabled=True,
    )
