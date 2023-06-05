from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import RedirectView


class LoginView(BaseLoginView):
    template_name = "login.jinja2"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("list_indicators"))
        else:
            return super().get(request, *args, **kwargs)


class RootView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return reverse("login")

        else:
            return reverse("list_indicators")
