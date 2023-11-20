from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt

from api import views as api_views
from autocomplete import HTMXAutoComplete

from cpho.urls import (
    urlpatterns as cpho_urls,  # force an import for runserver's refresh sake
)
from cpho.views.auth import LoginView, LogoutView, RootView

dev_routes = []
if settings.DEBUG and settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar

    dev_routes += [re_path(r"^__debug__/", include(debug_toolbar.urls))]

from phac_aspc.django.helpers.urls import urlpatterns as phac_aspc_helper_urls

urlpatterns = i18n_patterns(
    path("phac_admin/", admin.site.urls),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    *HTMXAutoComplete.url_dispatcher("ac"),
    path("", include(cpho_urls)),
    path(
        "graphiql/",
        csrf_exempt(api_views.GraphiQLView.as_view()),
        name="graphiql",
    ),
    path(
        "graphql/",
        csrf_exempt(api_views.GraphQLView.as_view()),
        name="graphql",
    ),
    prefix_default_language=False,
) + [
    *phac_aspc_helper_urls,
    path("healthcheck/", lambda r: HttpResponse(), name="simple_healthcheck"),
    path(
        "robots.txt",
        lambda r: HttpResponse(
            "User-Agent: *\nDisallow: /", content_type="text/plain"
        ),
        name="robots",
    ),
    re_path("^$", RootView.as_view(), name="root"),
    *dev_routes,
]
