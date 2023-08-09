from django.contrib import admin
from django.db import models

from server import fields
from server.model_util import add_to_admin

# from cpho.models import User
from cpho.text import tdt
from cpho.util import get_lang_code


def _get_phacorg_str(self, lang="en"):
    if lang == "fr":
        s = self.name_fr
    else:
        s = self.name_en
    if self.parent is None or self.parent_id == self.id:
        return s
    return f"{s} < {_get_phacorg_str(self.parent)}"


def _get_phacorg_acronym(self, lang="en"):
    if lang == "fr":
        acronym = self.acronym_fr
    else:
        acronym = self.acronym_en
    if self.parent is None or self.parent_id == self.id:
        return acronym
    return f"{_get_phacorg_acronym(self.parent)}-{acronym}"


@add_to_admin
class PHACOrg(models.Model):
    def __str__(self):
        s = _get_phacorg_acronym(self, get_lang_code())
        s += tdt("colon") + " "
        s += _get_phacorg_str(self, get_lang_code())
        return s

    class Meta:
        verbose_name = tdt("public_health_org")
        verbose_name_plural = tdt("public_health_orgs")

    class adminClass(admin.ModelAdmin):
        list_display = ("id",)
        list_editable = ()
        list_display_links = ("id",)

    id = models.CharField(max_length=10, primary_key=True)

    name_en = fields.CharField(max_length=200, default="")
    name_fr = fields.CharField(max_length=200, default="")
    acronym_en = fields.CharField(max_length=20, default="")
    acronym_fr = fields.CharField(max_length=20, default="")
    is_branch_lead = models.BooleanField(default=False)
    parent = fields.ForeignKey(
        "PHACOrg",
        related_name="children",
        null=True,
        on_delete=models.CASCADE,
    )

    @property
    def long_name(self):
        return _get_phacorg_str(self, get_lang_code())

    @property
    def acronym(self):
        return getattr(self, f"acronym_{get_lang_code()}")

    @property
    def full_acronym(self):
        return _get_phacorg_acronym(self, get_lang_code())

    @property
    def name(self):
        return getattr(self, f"name_{get_lang_code()}")
