from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)

from server.config_util import get_project_config, is_running_tests


def instrument_app():
    config = get_project_config()
    IS_LOCAL_DEV = config("IS_LOCAL_DEV", cast=bool, default=False)

    if is_running_tests():
        # TODO: maybe still instrument, just want to silence the output when the
        # test environment is detected
        return

    if IS_LOCAL_DEV:
        span_exporter = ConsoleSpanExporter()
    else:
        project_id = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/project/project-id",
            headers={"Metadata-Flavor": "Google"},
        ).text

        span_exporter = CloudTraceSpanExporter(
            project_id=project_id_response,
        )

    # a BatchSpanProcessor is better for performance but uses a background process,
    # which would require tricky and careful management in Cloud Run. Even in the best case,
    # I expect the necessary tricks would still result in the occasional dropped trace.
    # BatchSpanProcessor also requires extra configuration when combined with gunicorn's process forking
    span_processor = SimpleSpanProcessor(span_exporter)

    tracer_provider = TracerProvider(active_span_processor=span_processor)

    DjangoInstrumentor().instrument(
        tracer_provider=tracer_provider,
        meter_provider=None,  # TODO
        is_sql_commentor_enabled=True,
    )
