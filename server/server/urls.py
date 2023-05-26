from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path, re_path

from cpho.urls import (
    urlpatterns as cpho_urls,  # force an import for runserver's refresh sake
)
from cpho.views.auth import LoginView, LogoutView, RootView

dev_routes = []
if settings.DEBUG and settings.ENABLE_DEBUG_TOOLBAR:
    import debug_toolbar

    dev_routes += [re_path(r"^__debug__/", include(debug_toolbar.urls))]


urlpatterns = i18n_patterns(
    path("phac_admin/", admin.site.urls),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", include(cpho_urls)),
) + [
    re_path("^$", RootView.as_view(), name="root"),
    *dev_routes,
]
