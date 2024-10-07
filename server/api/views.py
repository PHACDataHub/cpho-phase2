import logging
import traceback

from graphene.validation import DisableIntrospection, depth_limit_validator
from graphene_django.views import GraphQLView as BaseGraphQLView
from graphql_core_promise import PromiseExecutionContext
from pleasant_promises.graphene import promised_generator_middleware

from server.middleware import AllowUnauthenticatedMixin

from .schema import schema
from .util import GraphQLContext

GRAPHQL_DEPTH_LIMIT = 5


class CustomGraphqlView(BaseGraphQLView):
    logger = logging.getLogger("django.request")
    schema = schema

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def as_view(cls, *args, **kwargs):
        new_kwargs = {
            "schema": cls.schema,
            "graphiql": False,
            "middleware": [promised_generator_middleware],
            "execution_context_class": PromiseExecutionContext,
            **kwargs,
        }
        return super().as_view(*args, **new_kwargs)

    def execute_graphql_request(self, *args, **kwargs):
        result = super().execute_graphql_request(*args, **kwargs)
        if result.errors:
            self._log_exceptions(result.errors)
        return result

    def _log_exceptions(self, errors):
        for error in errors:
            error_to_log = error
            if getattr(error, "original_error", None):
                error_to_log = error.original_error
            traceback_str = "".join(
                traceback.format_tb(error_to_log.__traceback__)
            )
            self.logger.error(
                f"{error_to_log.__class__.__name__}: {error_to_log}"
            )
            self.logger.error(traceback_str)

    def get_context(self, request):
        dataloaders = {}
        return GraphQLContext(dataloaders, user=self.request.user)


class GraphQLView(CustomGraphqlView, AllowUnauthenticatedMixin):
    """
    To be accessed in prod at /graphql
    """

    validation_rules = [depth_limit_validator(GRAPHQL_DEPTH_LIMIT)]

    pass


class GraphiQLView(CustomGraphqlView):
    """
    To be accessed in development at /graphiql
    """

    validation_rules = [
        # DisableIntrospection,
        depth_limit_validator(GRAPHQL_DEPTH_LIMIT),
    ]

    @classmethod
    def as_view(cls, *args, **kwargs):
        kwargs.update({"graphiql": True})
        return super().as_view(*args, **kwargs)
