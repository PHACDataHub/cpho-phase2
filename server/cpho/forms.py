from django.db.models import Q

from autocomplete import HTMXAutoComplete
from autocomplete import widgets as ac_widgets

from cpho.models import Indicator, IndicatorDirectory, User


class MultiIndicatorAutocomplete(HTMXAutoComplete):
    name = "indicators"
    multiselect = True
    minimum_search_length = 0
    model = Indicator

    def get_items(self, search=None, values=None):
        data = Indicator.objects.all()

        if search is not None:
            data = data.filter(
                Q(name__icontains=search)
                | Q(detailed_indicator__icontains=search)
                | Q(sub_indicator_measurement__icontains=search)
            )
            items = [{"label": str(x), "value": str(x.id)} for x in data]
            return items

        if values is not None:
            items = [
                {"label": str(x), "value": str(x.id)}
                for x in data
                if str(x.id) in values
            ]
            return items

        return []


class MultiUserAutocomplete(HTMXAutoComplete):
    name = "users"
    multiselect = True
    minimum_search_length = 0
    model = User

    def get_items(self, search=None, values=None):
        data = User.objects.all()

        if search is not None:
            filt = (
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(name__icontains=search)
            )
            data = data.filter(filt)

            items = [{"label": str(x), "value": str(x.id)} for x in data]
            return items

        if values is not None:
            items = [
                {"label": str(x), "value": str(x.id)}
                for x in data
                if str(x.id) in values
            ]
            return items

        return []
