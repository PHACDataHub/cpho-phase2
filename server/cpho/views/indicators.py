from django.forms.models import ModelForm
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from cpho.models import DimensionType, Indicator


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

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "dimension_types": DimensionType.objects.all(),
        }


class CreateIndicator(CreateView):
    model = Indicator
    form_class = IndicatorForm
    template_name = "indicators/create_indicator.jinja2"

    def get_success_url(self):
        return reverse("view_indicator", kwargs={"pk": self.object.pk})


class EditIndicator(UpdateView):
    model = Indicator
    form_class = IndicatorForm
    template_name = "indicators/edit_indicator.jinja2"

    def get_success_url(self):
        return reverse("view_indicator", kwargs={"pk": self.object.pk})
