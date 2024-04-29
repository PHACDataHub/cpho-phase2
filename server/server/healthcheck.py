from django.conf import settings
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor
from django.http import HttpResponse

from server.middleware import allow_unauthenticated


def _has_pending_migrations():
    db_alias = getattr(settings, "HEALTHCHECK_MIGRATIONS_DB", DEFAULT_DB_ALIAS)
    executor = MigrationExecutor(connections[db_alias])
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    if plan:
        return True

    return False


@allow_unauthenticated
def healthcheck_view(_request):
    if _has_pending_migrations():
        return HttpResponse("Database has pending migrations", status=503)

    return HttpResponse(status=200)
