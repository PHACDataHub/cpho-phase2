from django.contrib import messages
from django.db import transaction
from django.forms import BaseFormSet
from django.forms.formsets import formset_factory
from django.forms.models import ModelForm
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from cpho.models import DimensionType, Indicator, IndicatorDatum
from cpho.text import tdt, tm


class InstanceProvidingFormSet(BaseFormSet):
    """
    model formsets are tied to querysets. A queryset can't contain blank records
    so we use a custom formset and explicitely provide instances (some saved, some not)
    """

    def __init__(self, *args, instances=[], **kwargs):
        super().__init__(*args, **kwargs)
        self.instances = instances

    def get_form_kwargs(self, index):
        return {
            **super().get_form_kwargs(index),
            "instance": self.instances[index],
        }


class IndicatorDatumForm(ModelForm):
    class Meta:
        model = IndicatorDatum
        fields = ["value"]


class ManageIndicatorData(TemplateView):
    template_name = "indicator_data/manage_indicator_data.jinja2"

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["indicator_id"])

    @cached_property
    def dimension_type(self):
        return DimensionType.objects.prefetch_related("possible_values").get(
            id=self.kwargs["dimension_type_id"]
        )

    @cached_property
    def formset(self):
        existing_data = IndicatorDatum.objects.filter(
            indicator=self.indicator,
            dimension_value__dimension_type=self.dimension_type,
        ).order_by("dimension_value__order")

        existing_data_by_dimension_value = {
            datum.dimension_value: datum for datum in existing_data
        }

        possible_values = self.dimension_type.possible_values.all()

        instances = []
        for pv in possible_values:
            if existing_data_by_dimension_value.get(pv, None):
                record = existing_data_by_dimension_value[pv]
            else:
                record = IndicatorDatum(
                    indicator=self.indicator, dimension_value=pv
                )
            instances.append(record)

        factory = formset_factory(
            form=IndicatorDatumForm, formset=InstanceProvidingFormSet, extra=0
        )
        formset_kwargs = {
            "initial": [{} for x in possible_values],
            "instances": instances,
        }
        if self.request.POST:
            formset = factory(self.request.POST, **formset_kwargs)
        else:
            formset = factory(**formset_kwargs)

        return formset

    def post(self, *args, **kwargs):
        if self.formset.is_valid():
            with transaction.atomic():
                for form in self.formset:
                    form.save()

                messages.success(
                    self.request, tdt("Data saved."), messages.SUCCESS
                )
                return redirect(
                    "view_indicator",
                    pk=self.indicator.pk,
                )

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "indicator": self.indicator,
            "dimension_type": self.dimension_type,
            "formset": self.formset,
        }
