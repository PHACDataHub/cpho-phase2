import logging
import traceback

from django.db import connection

from api.schema import schema
from api.util import GraphQLContext
from graphene.test import Client
from graphql.error import GraphQLError
from graphql.language.parser import parse
from graphql.validation import validate
from graphql_core_promise import PromiseExecutionContext
from pleasant_promises.core import genfunc_to_prom, promise_from_generator
from pleasant_promises.graphene import promised_generator_middleware
from promise import Promise


def get_promise_result(func):
    """
    This is a helper function for testing dataloaders.
    Don't use it as a decorator but instead just call it directly:
    promised_result = get_promise_result(function_with_yields)

    """
    as_prom = genfunc_to_prom(func)
    prom = Promise.resolve(None).then(lambda _: as_prom())
    return prom.get()


class RaiseExceptionsMiddleware:
    logger = logging.getLogger("django.request")

    def on_error(self, error, *args, **kwargs):
        traceback_str = "".join(traceback.format_tb(error.__traceback__))
        self.logger.error(f"{error.__class__.__name__}: {error}")
        self.logger.error(traceback_str)

        raise error

    def resolve(self, next, root, info, **kwargs):
        return next(root, info, **kwargs)


class GraphQLExecutionErrorSet(Exception):
    def __init__(self, graphql_errors):
        self.graphql_errors = graphql_errors
        # err_str = json.dumps(graphql_errors, indent=4, sort_keys=True)
        super().__init__(graphql_errors)


class GraphqlExecutor:
    """
    - must define class variable "schema"

    if you want to execute multiple graphQL queries against the same data-loaders
    you must re-use instances of this class
    """

    schema = schema

    def __init__(self):
        self.client = Client(
            self.schema, execution_context_class=PromiseExecutionContext
        )
        self.dataloaders = {}

    def execute_query(
        self, query: str, root: any = None, variables: dict = None, user=None
    ):
        context = GraphQLContext(self.dataloaders, user)

        middleware = [
            RaiseExceptionsMiddleware(),
            promised_generator_middleware,
        ]

        resp = self.client.execute(
            query,
            root,
            context,
            variables,
            middleware=middleware,
        )

        if "errors" in resp:
            err = GraphQLExecutionErrorSet(resp["errors"])
            raise err
        return resp["data"]

    def build_query(self, query):
        validation_errors = validate(self.schema.graphql_schema, parse(query))
        if validation_errors:
            raise GraphQLError(validation_errors)

        def execute(*, context=None, **variables):
            return self.execute_query(query, context, variables=variables)

        return execute


def execute_query(query: str, variables: dict, user=None):
    executor = GraphqlExecutor()
    return executor.execute_query(query, variables=variables)
