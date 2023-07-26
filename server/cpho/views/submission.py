from django import forms
from django.contrib import messages
from django.core.exceptions import SuspiciousOperation, ValidationError
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

from .view_util import DimensionTypeOrAllMixin, SinglePeriodMixin


class SubmitIndicatorData(SinglePeriodMixin, DimensionTypeOrAllMixin, View):
    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["indicator_id"])

    def post(self, *args, **kwargs):
        # TODO: modify once we have users figured out
        # alternatively might want to make this a url or post param
        # so admins can approve as programs?

        if not (
            test_rule("is_admin", self.request.user)
            or (
                test_rule("is_program", self.request.user)
                and test_rule(
                    "can_submit_as_program", self.request.user, self.indicator
                )
            )
            or (
                test_rule("is_hso", self.request.user)
                and test_rule(
                    "can_submit_as_hso", self.request.user, self.indicator
                )
            )
        ):
            raise SuspiciousOperation(
                f"User {self.request.user} cannot review or submit this indicator"
            )

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
                "view_indicator_for_year",
                args=[self.indicator.id, self.period.id],
            ),
        )


class ReviewData(SinglePeriodMixin, DimensionTypeOrAllMixin, TemplateView):
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

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if not (
            test_rule("is_admin", request.user)
            or (
                test_rule("is_program", request.user)
                and test_rule(
                    "can_submit_as_program", request.user, self.indicator
                )
            )
            or (
                test_rule("is_hso", request.user)
                and test_rule(
                    "can_submit_as_hso", request.user, self.indicator
                )
            )
        ):
            raise SuspiciousOperation(
                f"User {request.user} cannot review or submit this indicator"
            )
        return self.render_to_response(context)
