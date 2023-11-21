import urllib

from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.views import View


class MustBeLoggedInMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        third_party_allow_unauthenticated_url_names = [
            "phac_aspc_helper_login",
            "phac_aspc_authorize",
        ]

        if getattr(view_func, "allow_unauthenticated", False) or (
            request.resolver_match.url_name
            in third_party_allow_unauthenticated_url_names
        ):
            return None

        if request.user.is_authenticated:
            return None
        elif "/login" not in request.path.lower():
            qs_params = dict(next=request.build_absolute_uri())
            querystring = urllib.parse.urlencode(qs_params)
            return HttpResponseRedirect(f"{settings.LOGIN_URL}?{querystring}")


def allow_unauthenticated(view_func):
    """
    decoractor for function-based-views to exempt them from the must-be-logged-in middleware
    """
    view_func.allow_unauthenticated = True
    return view_func


class AllowUnauthenticatedMixin(View):
    """
    mixin for function-based-views to exempt them from the must-be-logged-in middleware
    """

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super().as_view(*args, **kwargs)
        allow_unauthenticated(view)
        return view
