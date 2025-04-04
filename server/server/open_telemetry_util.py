import logging
import os
import sys
import time

import requests
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
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
from phac_aspc.django.helpers.logging.utils import (
    add_fields_to_all_logs_for_current_request,
)

from server.config_util import get_project_config, is_running_tests

logger = logging.getLogger()


def instrument_app_for_open_telemetry():
    config = get_project_config()

    IS_LOCAL = config("IS_LOCAL", cast=bool, default=False)
    FORCE_LOCAL_OTEL_BEHAVIOUR = config(
        "FORCE_LOCAL_OTEL_BEHAVIOUR", cast=bool, default=False
    )

    if IS_LOCAL or FORCE_LOCAL_OTEL_BEHAVIOUR:
        project_id = "local"

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
        # In Google Cloud, we must request resources information from a metadata server (metadata.google.internal).
        # In theory this is consistently reachable across GCP solutions (Cloud Run, App Engine, GKE, etc),
        # but in practice there's a big gotcha in GKE. New pods do not immediately have access to the metadata
        # server, and may not for a "few seconds" according to the docs linked below.
        # https://cloud.google.com/kubernetes-engine/docs/concepts/workload-identity#project_metadata
        #
        # Open telemetry "resource" information is used to identify the source of a span, and is imutable once
        # the corresponding trace provider has been initialized... which all needs to happen before the Django server
        # is initialized. This is all not ideal for cold start times! Not the slowest part though, running collect static
        # and migrations on pod start is a bigger slow down right now. Retrying the metadata.google.internal request with
        # a short linear delay is the best solution for now. Don't bother with exponential backoff because we want to know
        # asap and aren't worried about load on the metadata server (in theory; something to keep an eye on in practice).
        #
        # Note: we directly call metadata.google.internal below for the project ID, which _could_ be passed as
        # an env var, _but_ the GoogleCloudResourceDetector call following that also requires metadata server
        # access. GoogleCloudResourceDetector doesn't have the logic to wait for the metadata server so we need to
        # implement logic to wait for metadata.google.internal access our selves either way.
        retry_limit = 12
        retry_delay = 0.25

        logger.info("Attempting to connect to Google Cloud metadata server...")
        for retry_count in range(retry_limit):
            try:
                project_id = requests.get(
                    "http://metadata.google.internal/computeMetadata/v1/project/project-id",
                    headers={"Metadata-Flavor": "Google"},
                ).text

                break
            except requests.ConnectionError as error:
                if retry_count < retry_limit - 1:
                    time.sleep(retry_delay)
                else:
                    raise error
        logger.info("Metadata server reachable!")

        span_exporter = CloudTraceSpanExporter(
            project_id=project_id,
            # resource labels aren't exported in GCP by default, as the labels aren't actually supported
            # by Cloud Trace. This regex pattern is used to select resource labels to pick out and convert
            # to span attributes
            resource_regex=".*",
        )

        # WARNING: you might see examples wrapping a list of resource detectors in
        # `opentelemetry.sdk.resources.get_aggregated_resources`. This calls detect() and
        # merges the results for you BUT it uses thread pools and may not be suited for all
        # prod environments (Cloud Run, small k8s pods, etc).
        # Manually call detect and merge as needed instead, not a big deal, this only happens once
        # and isn't CPU intensive at all.
        # Note: for merge, the order matters with priority given to preceding resource objects
        resource = (
            GoogleCloudResourceDetector(raise_on_error=True).detect()
        ).merge(ProcessResourceDetector(raise_on_error=True).detect())

    # Propagate the X-Cloud-Trace-Context header if present. Add it otherwise
    set_global_textmap(CloudTraceFormatPropagator())

    # A BatchSpanProcessor is significantly better for performance, but has some caveats:
    #   1) gunicorn caveat: it uses a worker thread, which means instrumentation calls must happen post-gunicorn
    #   worker fork, or else multiple gunicron app worker threads will attempt to share one BatchSpanProcessor
    #   worker (and trip over eachother's process locks). Does not apply if gunicorn workers = threads = 1
    #   2) Cloud Run caveat: GCP docs say NOT to use BatchSpanProcessor in Cloud Run, as Cloud Run "does not
    #   support background processes". That is a simplification though, what they really mean is that a Cloud Run
    #   container will lose it's CPU when not actively processing a request, so background processes not tied to
    #   request handling may not have a chance to immediately finish all their work without interuption. They can
    #   still resume in the background when the container next receives a request. In the case that a container is
    #   terminated before receiving a new request, the container receives a SIGTERM signal and 10 seconds of grace time
    #   with a CPU to wrap things up (https://cloud.google.com/run/docs/container-contract#lifecycle-services).
    #   This caveat may apply in other auto-scalling environments
    #   The returned `flush_telemetry_callback` can be used to manage this if your environment requires.
    span_processor = BatchSpanProcessor(span_exporter)

    tracer_provider = TracerProvider(
        active_span_processor=span_processor,
        resource=resource,
        # Always sample, even if propagating a trace that wasn't sampled in earlier stages (load balancer, etc).
        # This could be too noisy on a busier app, but should be fine for CPHO's expected usage
        sampler=sampling.ALWAYS_ON,
    )

    def associate_request_logs_to_telemetry(span, request):
        add_fields_to_all_logs_for_current_request(
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
        # GOTCHA: in Cloud Run, if we disable our own instrumentation, I believe it just falls back to using
        # the default tracing Google has on Cloud Run instance... so you'll still get generic spans for excluded routes.
        # The default tracing is much lighter weight, so disabling does server _some_ purpose. This will also work as
        # expected in non-Cloud Run deployments
        excluded_urls=config(
            "OTEL_PYTHON_DJANGO_EXCLUDED_URLS", default="healthcheck"
        ),
        # Confusingly named (typo included), when True this actually adds a sqlcommenter django middleware.
        # When enabled, trace metadata is inserted as comments in each SQL query, allowing the corresponding logging
        # output on the DB side to be associated back to the initiating trace.
        # Currently disabled; may have a performance impact and, more importantly, currently causes test_infobase_export.py to fail
        is_sql_commentor_enabled=False,
    )

    def flush_telemetry_callback():
        tracer_provider.force_flush()
        tracer_provider.shutdown()

    return flush_telemetry_callback
