from autocomplete import ModelAutocomplete, register

from cpho import constants
from cpho.models import Indicator, User


@register
class IndicatorAutocomplete(ModelAutocomplete):
    minimum_search_length = 0
    model = Indicator
    search_attrs = ["name", "detailed_indicator", "sub_indicator_measurement"]


@register
class UserAutocomplete(ModelAutocomplete):
    minimum_search_length = 0
    model = User
    search_attrs = ["username", "email", "name"]

    @classmethod
    def get_queryset(cls):
        return super().get_queryset().exclude(is_staff=True)
