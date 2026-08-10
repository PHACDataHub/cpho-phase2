import re
from datetime import datetime

from django import forms
from django.contrib import messages
from django.forms.models import ModelForm
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from phac_aspc.rules import test_rule

from server.form_util import DescribedByErrorMixin, StandardFormMixin

from cpho.models import Indicator, TrendAnalysis
from cpho.text import tm
from cpho.util import get_regex_pattern
from cpho.views.view_util import (
    BaseInlineFormSetWithUniqueTogetherCheck,
    MustPassAuthCheckMixin,
    RequiredIfNotDeletedMixin,
)


class TrendAnalysisForm(
    RequiredIfNotDeletedMixin,
    ModelForm,
    StandardFormMixin,
    DescribedByErrorMixin,
):
    class Meta:
        model = TrendAnalysis
        fields = [
            "is_deleted",
            "year",
            "data_point",
            "line_of_best_fit_point",
            "trend_segment",
            "trend",
            "data_quality",
            "data_point_lower_ci",
            "data_point_upper_ci",
            "unit",
            "arrow_flag",
        ]

    year = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=tm("year"),
    )

    data_point = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        label=tm("data_point"),
    )

    line_of_best_fit_point = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        label=tm("line_of_best_fit_point"),
    )

    trend_segment = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=tm("trend_segment"),
    )

    trend = forms.ChoiceField(
        required=False,
        choices=TrendAnalysis.TREND_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("trend"),
    )

    data_quality = forms.ChoiceField(
        required=False,
        choices=TrendAnalysis.DATA_QUALITY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("data_quality"),
    )

    unit = forms.ChoiceField(
        required=False,
        choices=TrendAnalysis.UNIT_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("unit"),
    )

    data_point_lower_ci = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        label=tm("data_lower_ci"),
    )

    data_point_upper_ci = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        label=tm("data_upper_ci"),
    )

    arrow_flag = forms.ChoiceField(
        required=False,
        choices=TrendAnalysis.ARROW_FLAG_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("arrow_flag"),
    )

    is_deleted = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
        label=tm("delete"),
    )

    REQUIRED_UNLESS_DELETED = [
        "data_point",
        "year",
    ]

    def clean(self):
        super().clean()
        # if hasattr(self, "cleaned_data") and self.cleaned_data["is_deleted"]:
        #     self._errors = ErrorDict()
        is_deleted = self.cleaned_data.get("is_deleted", False)
        year = self.cleaned_data.get("year")
        data_point = self.cleaned_data.get("data_point")
        line_of_best_fit_point = self.cleaned_data.get(
            "line_of_best_fit_point"
        )
        trend_segment = self.cleaned_data.get("trend_segment")
        trend = self.cleaned_data.get("trend")
        data_quality = self.cleaned_data.get("data_quality")
        unit = self.cleaned_data.get("unit")
        data_point_lower_ci = self.cleaned_data.get("data_point_lower_ci")
        data_point_upper_ci = self.cleaned_data.get("data_point_upper_ci")

        if not is_deleted:
            # data_point
            if data_point is not None and data_point < 0:
                self.add_error(
                    "data_point",
                    tm("data_point_error"),
                )
            if (
                data_point_lower_ci is not None
                and data_point is not None
                and data_point_lower_ci > data_point
            ):
                self.add_error(
                    "data_point_lower_ci",
                    tm("data_point_lower_ci_error"),
                )
            if (
                data_point_upper_ci is not None
                and data_point is not None
                and data_point_upper_ci < data_point
            ):
                self.add_error(
                    "data_point_upper_ci",
                    tm("data_point_upper_ci_error"),
                )

            # individual field checks

            # year
            if year:
                single_year = re.match(
                    get_regex_pattern("trend_year_single")["pattern"], year
                )
                multi_year = re.match(
                    get_regex_pattern("trend_year_multi")["pattern"], year
                )

                if not single_year and not multi_year:
                    self.add_error(
                        "year",
                        tm("year_format"),
                    )

                else:
                    if single_year:
                        year_val = int(single_year.group(1))
                        if not (year_val >= 2000 and year_val <= 2050):
                            self.add_error(
                                "year",
                                tm("year_timeframe_between"),
                            )

                    else:
                        start_year = int(multi_year.group(1))
                        end_year = int(multi_year.group(2))
                        if not (2000 <= start_year <= end_year <= 2050):
                            self.add_error(
                                "year",
                                tm("year_timeframe_between_multi"),
                            )
                    self.cleaned_data["year"] = year.strip().replace(" ", "")

            # trend_segment
            if trend_segment:
                single_segment = re.match(
                    get_regex_pattern("trend_segment_single")["pattern"],
                    trend_segment,
                )
                multi_segment = re.match(
                    get_regex_pattern("trend_segment_multi")["pattern"],
                    trend_segment,
                )
                if not single_segment and not multi_segment:
                    self.add_error(
                        "trend_segment",
                        tm("trend_segment_format"),
                    )
                else:
                    if single_segment:
                        start_year = int(single_segment.group(1))
                        end_year = int(single_segment.group(2))
                        if not (2000 <= start_year <= end_year <= 2050):
                            self.add_error(
                                "trend_segment",
                                tm("trend_timeframe_between"),
                            )
                    else:
                        start_year_start = int(multi_segment.group(1))
                        start_year_end = int(multi_segment.group(2))
                        end_year_start = int(multi_segment.group(3))
                        end_year_end = int(multi_segment.group(4))
                        if (
                            not (
                                2000
                                <= start_year_start
                                <= end_year_end
                                <= 2050
                            )
                            or not (
                                2000
                                <= start_year_start
                                <= start_year_end
                                <= 2050
                            )
                            or not (
                                2000 <= end_year_start <= end_year_end <= 2050
                            )
                        ):
                            self.add_error(
                                "trend_segment",
                                tm("trend_timeframe_between_multi"),
                            )
                    self.cleaned_data["trend_segment"] = (
                        trend_segment.strip().replace(" ", "")
                    )

        return self.cleaned_data

    def save(self, commit=True):
        if self.cleaned_data["is_deleted"]:
            self.instance.deletion_time = str(datetime.now())
        return super().save(commit=commit)


class ManageTrendAnalysisData(MustPassAuthCheckMixin, TemplateView):
    template_name = "trend_analysis/manage_trend_analysis_data.jinja2"

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["indicator_id"])

    def check_rule(self):
        return test_rule(
            "can_edit_trend_analysis", self.request.user, self.indicator
        )

    def trend_analysis_formset(self):
        existing_data = TrendAnalysis.active_objects.filter(
            indicator=self.indicator
        ).order_by("year")

        InlineFormsetCls = forms.inlineformset_factory(
            Indicator,
            TrendAnalysis,
            fk_name="indicator",
            form=TrendAnalysisForm,
            extra=1,
            can_delete=False,
            formset=BaseInlineFormSetWithUniqueTogetherCheck,
        )

        kwargs = {
            "instance": self.indicator,
            "queryset": existing_data,
            "prefix": "trend_analysis",
        }

        if self.request.method == "POST":
            fs = InlineFormsetCls(self.request.POST, **kwargs)
        else:
            fs = InlineFormsetCls(**kwargs)

        for form in fs:
            form.instance.indicator = self.indicator

        return fs

    def post(self, *args, **kwargs):
        formset = self.trend_analysis_formset()
        if formset.is_valid():
            formset.save()
            messages.success(self.request, tm("saved_successfully"))
            return redirect(
                reverse(
                    "manage_trend_analysis_data",
                    kwargs={"indicator_id": self.indicator.id},
                )
            )
        else:
            print(formset.errors)
            messages.error(self.request, tm("error_saving_form"))
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["indicator"] = self.indicator
        context["trend_analysis_formset"] = self.trend_analysis_formset()
        return context
