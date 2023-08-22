import os
import sys

import requests
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.cloud_trace_propagator import (
    CloudTraceFormatPropagator,
)
from opentelemetry.resourcedetector.gcp_resource_detector import (
    GoogleCloudResourceDetector,
)
from opentelemetry.sdk.resources import ProcessResourceDetector
from opentelemetry.sdk.trace import TracerProvider, sampling
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from server.config_util import get_project_config, is_running_tests
from server.logging_util import add_metadata_to_all_logs_for_current_request


def instrument_app_for_open_telemetry():
    config = get_project_config()
    IS_LOCAL_DEV = config("IS_LOCAL_DEV", cast=bool, default=False)

    if IS_LOCAL_DEV:
        project_id = "local-dev"

        OUTPUT_TELEMETRY_TO_CONSOLE = config(
            "OUTPUT_TELEMETRY_TO_CONSOLE", cast=bool, default=False
        )

        span_exporter = ConsoleSpanExporter(
            out=(
                sys.stdout
                if OUTPUT_TELEMETRY_TO_CONSOLE
                else open(os.devnull, "w")
            )
        )

        resource = ProcessResourceDetector(raise_on_error=True).detect()
    else:
        project_id = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
        ).text

        span_exporter = CloudTraceSpanExporter(
            project_id=project_id,
            # resource attributes aren't exported in GCP by default, as they aren't actually supported
            # by Cloud Trace. This regex pattern is used to select resource attributes to covert and
            # upload as regular attributes
            resource_regex=".*",
        )

        # WARNING: you might see examples wrapping a list of resource detectors in
        # `opentelemetry.sdk.resources.get_aggregated_resources`. This calls detect() and
        # merges the results for you BUT it uses thread pools and may not be Cloud Run safe.
        # Manually call detect and merge as needed instead, not a big deal
        # Note for merge, the order matters with priority given to preceding resource objects
        resource = GoogleCloudResourceDetector(raise_on_error=True).detect()
        resource.merge(ProcessResourceDetector(raise_on_error=True).detect())

    # Propagate the X-Cloud-Trace-Context header if present. Add it otherwise
    set_global_textmap(CloudTraceFormatPropagator())

    # A BatchSpanProcessor is significantly better for performance, but has some caveats:
    #   1) gunicorn caveat: it uses a worker thread, which means instrumentation calls must happen post-gunicorn
    #   worker fork, or else multiple gunicron app worker threads will attempt to share one BatchSpanProcessor
    #   worker (and trip over eachother's process locks)
    #   2) Cloud Run caveat: GCP docs say NOT to use BatchSpanProcessor in Cloud Run, as Cloud Run "does not
    #   support background processes". That is a simplification though, what they really mean is that a Cloud Run
    #   container will lose it's CPU when not actively processing a request, so background processes not tied to
    #   request handling may not have a chance to immediately finish all their work without interuption. They can
    #   still resume in the background when the container next receives a request. In the case that a container is
    #   terminated before receiving a new request, the container receives a SIGTERM signal and 10 seconds of grace time
    #   with a CPU to wrap things up (https://cloud.google.com/run/docs/container-contract#lifecycle-services); see
    #   `flush_telemetry_callback` and its use in gunicorn.conf.py for how we take advantage of that
    span_processor = BatchSpanProcessor(span_exporter)

    tracer_provider = TracerProvider(
        active_span_processor=span_processor,
        resource=resource,
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

    Psycopg2Instrumentor().instrument(
        tracer_provider=tracer_provider,
        enable_commenter=True,
        commenter_options={},
        # This instrumentor expects the `psycopg2` package. This repo uses the `psycopg2-binary` package.
        # Compatible with both, but need to disable the instrumentor's dependency checking
        skip_dep_check=True,
    )

    DjangoInstrumentor().instrument(
        tracer_provider=tracer_provider,
        meter_provider=None,  # TODO
        request_hook=associate_request_logs_to_telemetry,
        # GOTCHA: in Cloud Run, if we disable our own instrumentation, I believe it just falls back to using
        # the default tracing Google has on Cloud Run instance... so you'll still get generic spans for excluded routes.
        # The default tracing is much lighter weight, so disabling does server _some_ purpose. This will also work as
        # expected in non-Cloud Run deployments
        excluded_urls=config(
            "OTEL_PYTHON_DJANGO_EXCLUDED_URLS", default="healthcheck"
        ),
        # confusingly named (typo included), this actually adds a sqlcommenter middleware, and is
        # redundant to the preferable Psycopg2Instrumentor commenter
        is_sql_commentor_enabled=False,
    )

    def flush_telemetry_callback():
        tracer_provider.force_flush()
        tracer_provider.shutdown()

    return flush_telemetry_callback
