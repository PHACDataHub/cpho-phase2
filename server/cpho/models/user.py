from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.functional import cached_property

from server import fields
from server.model_util import (
    add_to_admin,
    track_versions_with_editor,
    track_versions_with_editor_and_approval,
)


class GroupPrefetcherManager(UserManager):
    use_for_related_fields = True

    def get_queryset(self):
        return (
            super(GroupPrefetcherManager, self)
            .get_queryset()
            .prefetch_related(models.Prefetch("groups", to_attr="group_list"))
        )


@add_to_admin
class User(AbstractUser):
    class Meta:
        base_manager_name = "objects"

    objects = GroupPrefetcherManager()

    @cached_property
    def _all_groups(self):
        return list(self.groups.all())

    @property
    def group_names(self):
        return [g.name for g in self._all_groups]
