from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import BaseFormSet
from django.forms.formsets import formset_factory
from django.forms.models import ModelForm, inlineformset_factory
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import DetailView, TemplateView, View

from server.rules_framework import test_rule

from cpho.constants import (
    HSO_SUBMISSION_TYPE,
    PROGRAM_SUBMISSION_TYPE,
    SUBMISSION_STATUSES,
)
from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
)
from cpho.queries import get_submission_statuses
from cpho.services import SubmitIndicatorDataService
from cpho.text import tdt, tm
from cpho.util import group_by

from .view_util import (
    DimensionTypeOrAllMixin,
    MustPassAuthCheckMixin,
    SinglePeriodMixin,
)


class SubmitIndicatorData(
    MustPassAuthCheckMixin, SinglePeriodMixin, DimensionTypeOrAllMixin, View
):
    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["indicator_id"])

    def check_rule(self):
        return test_rule(
            "can_submit_as_hso_or_program",
            self.request.user,
            self.indicator,
        )

    def post(self, *args, **kwargs):
        # TODO: modify once we have users figured out
        # alternatively might want to make this a url or post param
        # so admins can approve as programs?

        submission_type = self.request.POST["submission_type"]

        SubmitIndicatorDataService(
            indicator=self.indicator,
            period=self.period,
            dimension_type=self.dimension_type,
            submission_type=submission_type,
            user=self.request.user,
        ).perform()
        messages.success(
            self.request, tdt("Submission successful"), messages.SUCCESS
        )
        return redirect(
            reverse(
                "view_indicator_for_period",
                args=[self.indicator.id, self.period.id],
            ),
        )


class ReviewData(
    MustPassAuthCheckMixin,
    SinglePeriodMixin,
    DimensionTypeOrAllMixin,
    TemplateView,
):
    model = Indicator
    template_name = "review_data.jinja2"

    @cached_property
    def indicator(self):
        return get_object_or_404(Indicator, pk=self.kwargs["indicator_id"])

    @cached_property
    def indicator_data(self):
        qs = (
            self.indicator.data.filter(period=self.period)
            .select_related("dimension_value")
            .prefetch_related("dimension_type")
            .with_submission_annotations()
            .with_last_version_date()
            .order_by("dimension_value")
        )

        if self.dimension_type:
            qs = qs.filter(dimension_type=self.dimension_type)

        return qs

    @cached_property
    def indicator_data_by_dimension_type(self):
        return group_by(
            list(self.indicator_data), lambda d: d.dimension_type_id
        )

    @cached_property
    def submission_statuses(self):
        return get_submission_statuses(self.indicator, self.period)

    @cached_property
    def submission_status(self):
        if self.dimension_type:
            return self.submission_statuses["statuses_by_dimension_type_id"][
                self.dimension_type.id
            ]
        else:
            return self.submission_statuses["global_status"]

    @cached_property
    def dimension_types(self):
        qs = DimensionType.objects.all()
        if self.dimension_type:
            qs = qs.filter(pk=self.dimension_type.pk)
        return qs

    def get_context_data(self, *args, **kwargs):
        return {
            **super().get_context_data(*args, **kwargs),
        }

    def check_rule(self):
        return test_rule(
            "can_submit_as_hso_or_program",
            self.request.user,
            self.indicator,
        )
