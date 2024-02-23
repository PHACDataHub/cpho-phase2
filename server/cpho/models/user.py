from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.functional import cached_property

from server import fields
from server.model_util import (
    add_to_admin,
    track_versions_with_editor,
    track_versions_with_editor_and_submission,
)

from cpho.constants import ADMIN_GROUP_NAME, HSO_GROUP_NAME
from cpho.text import tm


class GroupPrefetcherManager(UserManager):
    use_for_related_fields = True

    def get_queryset(self):
        return (
            super(GroupPrefetcherManager, self)
            .get_queryset()
            .prefetch_related("groups")
        )


@add_to_admin
class User(AbstractUser):
    class Meta:
        base_manager_name = "objects"

    def __str__(self):
        return f"{self.name if self.name else self.username}"

    objects = GroupPrefetcherManager()

    name = models.CharField(tm("name"), max_length=300, blank=True)

    @property
    def pretty_name(self):
        if not self.name:
            return self.username

        # attempts to show firstname lastname
        w_out_phac_suffix = self.name.replace("(PHAC/ASPC)", "").strip()

        if ", " in w_out_phac_suffix:
            last, first = w_out_phac_suffix.split(", ")
            return f"{first} {last}"

        return w_out_phac_suffix

    @cached_property
    def _all_groups(self):
        return list(self.groups.all())

    @property
    def group_names(self):
        return [g.name for g in self._all_groups]

    @property
    def is_hso(self):
        return HSO_GROUP_NAME in self.group_names

    @property
    def is_admin(self):
        return ADMIN_GROUP_NAME in self.group_names
