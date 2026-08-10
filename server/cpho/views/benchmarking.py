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

from cpho.models import Benchmarking, Country, Indicator
from cpho.text import tm
from cpho.util import get_regex_pattern
from cpho.views.view_util import (
    BaseInlineFormSetWithUniqueTogetherCheck,
    MustPassAuthCheckMixin,
    ReadOnlyFormMixin,
    RequiredIfNotDeletedMixin,
)


class BenchmarkingForm(
    RequiredIfNotDeletedMixin,
    ModelForm,
    DescribedByErrorMixin,
    StandardFormMixin,
):
    class Meta:
        model = Benchmarking
        fields = [
            "is_deleted",
            "indicator",
            "unit",
            "oecd_country",
            "value",
            "year",
            "comparison_to_oecd_avg",
            "labels",
            "methodology_differences",
        ]

    is_deleted = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
        label=tm("delete"),
    )

    unit = forms.ChoiceField(
        required=False,
        choices=Benchmarking.UNIT_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("unit"),
    )

    oecd_country = forms.ModelChoiceField(
        required=False,
        queryset=Country.objects.all().order_by("name_en"),
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("oecd_country"),
    )

    value = forms.FloatField(
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": tm("value")}
        ),
        label=tm("value"),
    )
    year = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label=tm("year"),
    )

    comparison_to_oecd_avg = forms.ChoiceField(
        required=False,
        choices=Benchmarking.COMPARISON_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("comparison_to_oecd_average"),
    )
    labels = forms.ChoiceField(
        required=False,
        choices=Benchmarking.LABEL_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
        label=tm("labels"),
    )

    methodology_differences = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
        label=tm("methodology_differences"),
    )

    REQUIRED_UNLESS_DELETED = [
        "oecd_country",
        "value",
        "comparison_to_oecd_avg",
    ]

    def clean(self):
        super().clean()
        # if hasattr(self, "cleaned_data") and self.cleaned_data["is_deleted"]:
        #     self._errors = ErrorDict()

        is_deleted = self.cleaned_data.get("is_deleted", False)
        indicator = self.cleaned_data.get("indicator")
        unit = self.cleaned_data.get("unit")
        oecd_country = self.cleaned_data.get("oecd_country")
        value = self.cleaned_data.get("value")
        year = self.cleaned_data.get("year")
        comparison_to_oecd_avg = self.cleaned_data.get(
            "comparison_to_oecd_avg"
        )
        labels = self.cleaned_data.get("labels")
        methodology_differences = self.cleaned_data.get(
            "methodology_differences", False
        )

        if not is_deleted:
            # value
            if value and value < 0:
                self.add_error("value", tm("value_cannot_be_negative"))

            # year is required for all countries except OECD
            if year is None or year == "":
                if oecd_country and not oecd_country.name_en in [
                    "OECD Average"
                ]:
                    self.add_error(
                        "year",
                        tm("year_required"),
                    )
            # year in the format mm/yyyy covid-19 deaths
            if year:
                if indicator.id == 168:
                    pattern = get_regex_pattern("benchmarking_year")["pattern"]
                    match = re.match(pattern, year)
                    if not match:
                        self.add_error(
                            "year",
                            tm("year_format_mm_yyyy"),
                        )
                    if match:
                        month = int(match.group(1).strip())
                        if not (month >= 1 and month <= 12):
                            self.add_error(
                                "year",
                                tm("month_format"),
                            )
                        _year = int(match.group(2).strip())
                        if not (_year >= 2000 and _year <= 2050):
                            self.add_error(
                                "year",
                                tm("year_timeframe_between"),
                            )
                        self.cleaned_data["year"] = str(year).strip()
                else:
                    try:
                        if not (int(year) >= 2000 and int(year) <= 2050):
                            self.add_error(
                                "year",
                                tm("year_timeframe_between"),
                            )
                    except ValueError:
                        self.add_error(
                            "year",
                            tm("year_must_be_number"),
                        )

        return self.cleaned_data

    def save(self, commit=True):
        if self.cleaned_data["is_deleted"]:
            self.instance.deletion_time = str(datetime.now())
        return super().save(commit=commit)


class ReadOnlyBenchmarkingForm(BenchmarkingForm, ReadOnlyFormMixin):
    """A form for the read only benchmarking view."""

    def __init__(self, *args, **kwargs):
        super(ReadOnlyBenchmarkingForm, self).__init__(*args, **kwargs)
        self.choice_to_text_field()
        self.disable_fields()
        self.remove_placeholders()


class ManageBenchmarkingData(MustPassAuthCheckMixin, TemplateView):
    template_name = "benchmarking/manage_benchmarking_data.jinja2"

    @cached_property
    def indicator(self):
        return Indicator.objects.get(pk=self.kwargs["indicator_id"])

    def check_rule(self):
        return test_rule(
            "can_view_benchmarking", self.request.user, self.indicator
        )

    def benchmarking_formset(self):
        existing_data = Benchmarking.active_objects.filter(
            indicator=self.indicator
        ).order_by("labels", "-value")

        form_type = ReadOnlyBenchmarkingForm
        extra_val = 0
        if test_rule(
            "can_edit_benchmarking", self.request.user, self.indicator
        ):
            form_type = BenchmarkingForm
            extra_val = 1

        InlineFormsetCls = forms.inlineformset_factory(
            Indicator,
            Benchmarking,
            fk_name="indicator",
            form=form_type,
            extra=extra_val,
            can_delete=False,
            formset=BaseInlineFormSetWithUniqueTogetherCheck,
        )

        kwargs = {
            "instance": self.indicator,
            "queryset": existing_data,
            "prefix": "benchmarking",
        }

        if self.request.method == "POST":
            fs = InlineFormsetCls(self.request.POST, **kwargs)
        else:
            fs = InlineFormsetCls(**kwargs)

        for form in fs:
            form.instance.indicator = self.indicator

        return fs

    def post(self, *args, **kwargs):
        formset = self.benchmarking_formset()
        if formset.is_valid():
            formset.save()
            messages.success(self.request, tm("saved_successfully"))
            return redirect(
                reverse(
                    "manage_benchmarking_data",
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
        context["benchmarking_formset"] = self.benchmarking_formset()
        return context
