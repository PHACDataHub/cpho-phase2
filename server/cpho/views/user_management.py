from typing import Any, Dict

from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import (
    CreateView,
    FormView,
    TemplateView,
    UpdateView,
    View,
)

from autocomplete import AutocompleteWidget
from phac_aspc.rules import test_rule

from server.form_util import StandardFormMixin

from cpho.constants import ADMIN_GROUP_NAME, HSO_GROUP_NAME
from cpho.forms import IndicatorAutocomplete, UserAutocomplete
from cpho.models import (
    DimensionType,
    Indicator,
    IndicatorDirectory,
    Period,
    User,
)
from cpho.text import tdt, tm
from cpho.util import (
    GroupFetcher,
    get_lang_code,
    get_or_create_user_by_email,
    is_allowed_email,
    phac_email_widget_attrs,
)

from .view_util import MustPassAuthCheckMixin


class CanManageUsersMixin(MustPassAuthCheckMixin):
    def check_rule(self):
        return test_rule(
            "can_manage_users",
            self.request.user,
        )


class ManageUsers(CanManageUsersMixin, TemplateView):
    template_name = "user_management/user_management_page.jinja2"

    def get_context_data(self, **kwargs):
        all_users = User.objects.all()

        indicator_directories = (
            IndicatorDirectory.objects.all().prefetch_related(
                "users", "indicators"
            )
        )

        return {
            **super().get_context_data(**kwargs),
            "all_users": all_users,
            "indicator_directories": indicator_directories,
        }


class UserForm(forms.Form):
    is_admin = forms.BooleanField(
        required=False,
        label=tdt("Super user"),
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )
    is_hso = forms.BooleanField(
        required=False,
        label=tdt("HSO User"),
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )


class CreateUserForm(UserForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={**phac_email_widget_attrs}),
    )
    email_confirmation = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={**phac_email_widget_attrs}),
    )

    def clean_email(self):
        # force only lowercase emails, safer to compare that way
        email = self.cleaned_data["email"].lower()
        if not is_allowed_email(email):
            raise ValidationError(tdt("email_exception"))

        if User.objects.filter(email__icontains=email).exists():
            raise ValidationError(tdt("account_for_email_already_exists"))

        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        email_confirmation = cleaned_data.get("email_confirmation")

        if email != email_confirmation:
            raise ValidationError(tm("email_confirmation_exception"))

        return cleaned_data


class UserFormView(FormView, CanManageUsersMixin):
    template_name = "user_management/create_modify_user.jinja2"

    def form_valid(self, form):
        self.save_form(form)
        self.show_message()
        return super().form_valid(form)

    def show_message(self):
        raise NotImplementedError()

    def get_success_url(self):
        return reverse("manage_users")

    def get_or_create_user(self, form):
        raise NotImplementedError()

    def save_form(self, form):
        with transaction.atomic():
            user = self.get_or_create_user(form)
            self.assign_groups(user, form)

    def assign_groups(self, user, form):
        user.groups.remove(
            GroupFetcher.hso_group,
            GroupFetcher.admin_group,
        )

        if form.cleaned_data["is_admin"]:
            user.groups.add(GroupFetcher.admin_group)

        if form.cleaned_data["is_hso"]:
            user.groups.add(GroupFetcher.hso_group)


class CreateUser(UserFormView, CanManageUsersMixin):
    def get_form(self):
        if self.request.POST:
            return CreateUserForm(self.request.POST)
        else:
            return CreateUserForm()

    def get_or_create_user(self, form):
        email = form.cleaned_data["email"]
        return User.objects.create_user(
            email=email, username=email, password=email
        )

    def show_message(self):
        messages.success(self.request, tdt("user created"))

    def get_initial(self):
        return {}


class ModifyUser(UserFormView, CanManageUsersMixin):
    def get_form(self):
        form_initial = self.get_initial()
        if self.request.POST:
            return UserForm(self.request.POST, initial=form_initial)
        else:
            return UserForm(initial=form_initial)

    def get_initial(self):
        user = User.objects.get(id=self.kwargs["user_id"])
        initial = {
            "is_admin": user.is_admin,
            "is_hso": user.is_hso,
        }
        return initial

    def get_or_create_user(self, form):
        return User.objects.get(id=self.kwargs["user_id"])

    def show_message(self):
        messages.success(self.request, tdt("user modified"))

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "user_to_be_modified": User.objects.get(id=self.kwargs["user_id"]),
        }


class IndicatorDirectoryForm(forms.ModelForm, StandardFormMixin):
    class Meta:
        model = IndicatorDirectory
        fields = ["name", "description", "indicators", "users"]

    indicators = forms.ModelMultipleChoiceField(
        queryset=Indicator.objects.all(),
        required=False,
        widget=AutocompleteWidget(
            ac_class=IndicatorAutocomplete,
            options={
                "multiselect": True,
            },
        ),
        label=tdt("indicators"),
    )

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=AutocompleteWidget(
            ac_class=UserAutocomplete,
            options={
                "multiselect": True,
            },
        ),
        label=tdt("users"),
    )


class IndicatorDirectoryFormMixin(FormView):
    form_class = IndicatorDirectoryForm
    template_name = "user_management/create_modify_indicator_directory.jinja2"

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs["instance"] = self.directory_object
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("root")


class CreateIndicatorDirectory(
    CanManageUsersMixin, IndicatorDirectoryFormMixin
):
    @cached_property
    def directory_object(self):
        return IndicatorDirectory()


class EditIndicatorDirectory(CanManageUsersMixin, IndicatorDirectoryFormMixin):
    @cached_property
    def directory_object(self):
        return IndicatorDirectory.objects.get(id=self.kwargs["pk"])


class EmailForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                **phac_email_widget_attrs,
            }
        ),
    )
    email_confirmation = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={**phac_email_widget_attrs}),
    )

    def clean_email(self):
        # force only lowercase emails, safer to compare that way
        email = self.cleaned_data["email"].lower()
        if not is_allowed_email(email):
            raise ValidationError(tdt("email_exception"))

        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        email_confirmation = cleaned_data.get("email_confirmation")

        if email != email_confirmation:
            raise ValidationError(tm("email_confirmation_exception"))

        return cleaned_data


class IndicatorDirectoryHome(FormView):
    form_class = EmailForm
    template_name = "user_management/indicator_directory_home.jinja2"

    def get_context_data(self, **kwargs: Any):
        return {
            **super().get_context_data(**kwargs),
            "indicator_directory": self.indicator_directory,
        }

    @cached_property
    def indicator_directory(self):
        return IndicatorDirectory.objects.get(id=self.kwargs["pk"])

    def dispatch(self, request, *args, **kwargs):
        if not test_rule(
            "can_access_indicator_directory",
            request.user,
            self.indicator_directory.id,
        ):
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = get_or_create_user_by_email(email)
        self.indicator_directory.users.add(user)
        messages.success(
            self.request, tdt("user added to indicator directory")
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("indicator_directory_home", args=[self.kwargs["pk"]])
