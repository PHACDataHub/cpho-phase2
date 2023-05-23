"""
This contains custom fields that should be used in place of the default Django fields.

The django migration engines serializes all fields and their attributes. 
There are many attributes that are not relevant to the database schema. The fields below override serialization and strip irrelevant attributes.

These fields strip attributes from serialization so we don't get extra migrations when we change verbose names or related_names

"""

from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

migration_ignored_attrs = [
    "help_text",
    "is_searchable",
    "description",
    "verbose_name",
    "verbose_name_plural",
    "ordering",
    "validators",
    "blank",
    "extra_options",
    "related_name",
    "choices",
]


class SearchableFieldMixin:
    def __init__(self, *args, is_searchable=False, **kwargs):
        self.is_searchable = is_searchable
        super().__init__(*args, **kwargs)


class DescriptionMixin:
    def __init__(self, *args, extra_options=None, description="", **kwargs):
        self.extra_options = extra_options or {}
        self.description = description
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        for attr in migration_ignored_attrs:
            kwargs.pop(attr, None)
        return name, path, args, kwargs


class ManyToManyField(DescriptionMixin, models.ManyToManyField):
    pass


# if you want to ensure NULLs get replaced with empty string "", pass null_to_empty to CharField/TextField
class EmptyToNullMixin:
    def __init__(self, *args, null_to_empty=False, **kwargs):
        if null_to_empty:
            bad_keys = [
                "choices",
                "null",
                "default",
                "dbindex",
                "primary_key",
                "unique",
            ]
            if any(key in kwargs for key in bad_keys):
                raise Exception(
                    " Improper use of fields, you probably want a NULL-able column"
                )

            super().__init__(
                *args,
                null=False,
                default="",
                **kwargs,
            )

        else:
            super().__init__(*args, **kwargs)


class CharField(
    SearchableFieldMixin, DescriptionMixin, EmptyToNullMixin, models.CharField
):
    pass


class TextField(
    SearchableFieldMixin, DescriptionMixin, EmptyToNullMixin, models.TextField
):
    def deconstruct(self):
        # according to django docs, TextField char-limits are not enforced at the DB level
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop("max_length", None)

        return name, path, args, kwargs


class ForeignKey(DescriptionMixin, models.ForeignKey):
    pass


choices_by_type = {
    "yes_or_no": ((True, "yes"), (False, "no")),
    "true_or_false": ((True, "true"), (False, "false")),
}


class BooleanField(DescriptionMixin, models.BooleanField):
    def __init__(self, *args, **kwargs):
        if "choices" not in kwargs:
            # default to True/False
            choice_type = kwargs.pop("choice_type", "yes_or_no")
            kwargs["choices"] = choices_by_type[choice_type]

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop("choices", None)
        kwargs.pop("choice_type", None)

        return name, path, args, kwargs


class DecimalField(DescriptionMixin, models.DecimalField):
    pass


class FloatField(DescriptionMixin, models.FloatField):
    pass


class IntegerField(DescriptionMixin, models.IntegerField):
    pass


class PositiveIntegerField(DescriptionMixin, models.PositiveIntegerField):
    pass


class SlugField(DescriptionMixin, models.SlugField):
    pass


class OneToOneField(DescriptionMixin, models.OneToOneField):
    pass


class AutoField(DescriptionMixin, models.AutoField):
    pass


class BigAutoField(DescriptionMixin, models.BigAutoField):
    pass


class DateTimeField(DescriptionMixin, models.DateTimeField):
    pass


class DateField(DescriptionMixin, models.DateField):
    pass


class EmailField(DescriptionMixin, models.EmailField):
    pass


class URLField(DescriptionMixin, models.URLField):
    pass


class ImageField(DescriptionMixin, models.ImageField):
    pass


class FileField(DescriptionMixin, models.FileField):
    pass
