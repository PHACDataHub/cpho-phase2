from typing import Any, Dict

from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
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

from autocomplete import HTMXAutoComplete
from autocomplete import widgets as ac_widgets

from server.form_util import StandardFormMixin
from server.rules_framework import test_rule

from cpho.constants import ADMIN_GROUP_NAME, HSO_GROUP_NAME
from cpho.forms import MultiIndicatorAutocomplete, MultiUserAutocomplete
from cpho.models import (
    DimensionType,
    Indicator,
    IndicatorDirectory,
    Period,
    PHACOrg,
    PhacOrgRole,
    User,
)
from cpho.text import tdt
from cpho.util import GroupFetcher, get_lang_code

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
        user_metadata = {}
        all_users = User.objects.all()

        for user in all_users:
            user_phac_org_roles = PhacOrgRole.objects.filter(user=user)
            role_metadata = []
            for roles in user_phac_org_roles:
                role_metadata.append(
                    {
                        "phac_org_obj": roles.phac_org,
                        "phac_org_name": roles.phac_org.name_en
                        if get_lang_code() == "en"
                        else roles.phac_org.name_fr,
                        "is_lead": roles.is_phac_org_lead,
                    }
                )
            user_metadata[user] = role_metadata

        indicator_directories = (
            IndicatorDirectory.objects.all().prefetch_related(
                "users", "indicators"
            )
        )

        return {
            **super().get_context_data(**kwargs),
            "user_metadata": user_metadata,
            "indicator_directories": indicator_directories,
        }


class MultiPhacOrgAutocomplete(HTMXAutoComplete):
    """Autocomplete component to select phacOrgs"""

    name = "phac_org_multi"
    multiselect = True
    minimum_search_length = 0
    model = PHACOrg

    def get_items(self, search=None, values=None):
        data = PHACOrg.branches().select_related(
            "parent", "parent__parent", "parent__parent__parent"
        )
        if search is not None:
            items = [
                {"label": str(x), "value": str(x.id)}
                for x in data
                if search == "" or str(search).upper() in f"{x}".upper()
            ]
            return items
        if values is not None:
            items = [
                {"label": str(x), "value": str(x.id)}
                for x in data
                if str(x.id) in values
            ]
            return items

        return []


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

    phac_org_multi = forms.ModelMultipleChoiceField(
        queryset=PHACOrg.branches(),
        required=False,
        widget=ac_widgets.Autocomplete(
            use_ac=MultiPhacOrgAutocomplete,
            attrs={
                "id": "phac_org_multi__textinput",
            },
        ),
        label=tdt("phac_org_multi"),
    )


class CreateUserForm(UserForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                # Only allow emails ending in @*.gc.ca or @canada.ca
                "pattern": r"^[a-zA-Z0-9_.+\-]+@([a-zA-Z0-9\-]+\.gc\.ca|canada\.ca)$",
                "oninvalid": f"setCustomValidity('{tdt('invalid email use phac-aspc.gc.ca or canada.ca')}')",
                "oninput": "setCustomValidity('')",
                "class": "form-control",
            }
        ),
    )

    def clean_email(self):
        # force only lowercase emails, safer to compare that way
        email = self.cleaned_data["email"].lower()
        if not (email.endswith("@canada.ca") or email.endswith(".gc.ca")):
            raise ValidationError(tdt("email_exception"))

        if User.objects.filter(email__icontains=email).exists():
            raise ValidationError(tdt("account_for_email_already_exists"))

        return email


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
            self.assign_orgs(user, form)
            self.assign_groups(user, form)

    def assign_orgs(self, user, form):
        user.phac_org_roles.all().delete()
        for org in form.cleaned_data["phac_org_multi"]:
            # TODO: if we keep branch leads, split this out into 2 fields, branches_lead and branches_read_only
            PhacOrgRole.objects.create(
                user=user, phac_org=org, is_phac_org_lead=True
            )

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
            "phac_org_multi": [r.phac_org for r in user.phac_org_roles.all()],
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
        widget=ac_widgets.Autocomplete(
            use_ac=MultiIndicatorAutocomplete,
            attrs={
                "id": "indicators__textinput",
            },
        ),
        label=tdt("indicators"),
    )

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=ac_widgets.Autocomplete(
            use_ac=MultiUserAutocomplete,
            attrs={
                "id": "users__textinput",
            },
        ),
        label=tdt("users"),
    )


class IndicatorDirectoryMixin(FormView):
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


class CreateIndicatorDirectory(CanManageUsersMixin, IndicatorDirectoryMixin):
    @cached_property
    def directory_object(self):
        return IndicatorDirectory()


class EditIndicatorDirectory(CanManageUsersMixin, IndicatorDirectoryMixin):
    @cached_property
    def directory_object(self):
        return IndicatorDirectory.objects.get(id=self.kwargs["pk"])
