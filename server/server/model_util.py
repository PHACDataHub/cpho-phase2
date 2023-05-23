import importlib

from django.conf import settings
from django.db import models
from django.utils import timezone

from versionator import VersionModel


def add_to_admin(cls):
    cls.__add_to_admin = True
    return cls


class CustomVersionModel(VersionModel):
    class Meta:
        abstract = True
        ordering = ["business_date"]
        get_latest_by = "business_date"

    # for legacy reasons (changelog support) we need 2 identical columns called system_date and business_date
    system_date = models.DateTimeField(default=timezone.now)
    business_date = models.DateTimeField(default=timezone.now)

    @property
    def previous_version(self):
        return (
            self.__class__.objects.filter(
                eternal_id=self.eternal_id,
                business_date__lt=self.business_date,
            )
            .order_by("business_date")
            .last()
        )

    @classmethod
    def get_fields_to_version(cls):
        return [f for f in cls.live_model._meta.fields if f.concrete]


class CustomVersionModelWithEditor(CustomVersionModel):
    class Meta(CustomVersionModel.Meta):
        abstract = True

    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )


class ApprovableCustomVersionModelWithEditor(CustomVersionModelWithEditor):
    class Meta(CustomVersionModelWithEditor.Meta):
        abstract = True

    approved = models.BooleanField(default=False)


def create_history_decorator(version_base_class):
    """
    The most common use case is to not customize the history class at all,
    pick a standardized model name, and register it on the admin
    """

    def decorator(live_model):
        version_cls_name = f"{live_model.__name__}History"
        version_model_cls = type(
            version_cls_name,
            (version_base_class,),
            {"live_model": live_model, "__module__": live_model.__module__},
        )
        setattr(
            importlib.import_module(live_model.__module__),
            version_cls_name,
            version_model_cls,
        )

        # version_model_cls.adminClass = create_default_admin_class(live_model)
        add_to_admin(version_model_cls)

        return live_model

    return decorator


track_versions = create_history_decorator(CustomVersionModel)
track_versions_with_editor = create_history_decorator(
    CustomVersionModelWithEditor
)
track_versions_with_editor_and_approval = create_history_decorator(
    ApprovableCustomVersionModelWithEditor
)
