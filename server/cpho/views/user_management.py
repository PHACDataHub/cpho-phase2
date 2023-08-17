from django.views.generic import TemplateView

from server.rules_framework import test_rule

from cpho.models import (
    DimensionType,
    Indicator,
    Period,
    PHACOrg,
    PhacOrgRole,
    User,
)
from cpho.util import get_lang_code

from .view_util import MustPassAuthCheckMixin


class ManageUsers(MustPassAuthCheckMixin, TemplateView):
    template_name = "user_management/user_management_page.jinja2"

    def check_rule(self):
        return test_rule(
            "can_manage_users",
            self.request.user,
        )

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

        return {
            **super().get_context_data(**kwargs),
            "user_metadata": user_metadata,
        }
