from cpho.models import Indicator
from django.forms.models import ModelForm
from django.views.generic import CreateView, DetailView, ListView, UpdateView


class IndicatorForm(ModelForm):
    class Meta:
        model = Indicator
        fields = "__all__"


class ListIndicators(ListView):
    model = Indicator
    template_name = "indicators/list_indicators.jinja2"


class ViewIndicator(DetailView):
    model = Indicator
    template_name = "indicators/view_indicator.jinja2"


class CreateIndicator(CreateView):
    model = Indicator
    form_class = IndicatorForm
    template_name = "indicators/create_indicator.jinja2"


class EditIndicator(UpdateView):
    model = Indicator
    form_class = IndicatorForm
    template_name = "indicators/edit_indicator.jinja2"
