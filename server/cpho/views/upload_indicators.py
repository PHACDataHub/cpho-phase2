import csv
from typing import Any

from django import forms
from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import FormView, TemplateView, View

from phac_aspc.rules import test_rule

from cpho import mapping_util
from cpho.mapping_util import ImportMapper
from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
    Period,
)
from cpho.text import tdt, tm

from .view_util import IndDataCleaner, MustPassAuthCheckMixin


class UploadForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    csv_file = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    def save(self):
        data = self.cleaned_data["csv_file"]
        self.request.session["upload_data"] = data

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        if not csv_file.name.endswith(".csv"):
            raise forms.ValidationError(tdt("File is not CSV type"))
        if csv_file.multiple_chunks():
            raise forms.ValidationError(
                tdt("Uploaded file is too big. Maximum size allowed is 2 MB")
            )
        file_data = csv_file.read()
        # keeping this print in here because the output is useful for adding to test_upload.py
        # print(file_data)
        file_data = file_data.decode("utf-8-sig").splitlines()
        reader = csv.DictReader(file_data)
        data_dict = []
        required_headers = [
            "Category",
            "Topic",
            "Indicator",
            "Detailed Indicator",
            "Sub_Indicator_Measurement",
            "Data_Quality",
            "Value",
            "Value_LowerCI",
            "Value_UpperCI",
            "Value_Displayed",
            "SingleYear_TimeFrame",
            "MultiYear_TimeFrame",
            "Dimension_Type",
            "Dimension_Value",
            "Period",
            "Reason_for_Null_Data",
            "Value_Units",
            "Arrow_Flag",
        ]
        missing_headers = []
        for header in required_headers:
            if header not in reader.fieldnames:
                missing_headers.append(header)
        if missing_headers:
            raise forms.ValidationError(
                f"{tm('file_is_missing_the_required_columns')} : {', '.join(missing_headers)}"
            )

        errorlist = []
        # checking for invalid values in the csv
        for idx, data_row in enumerate(reader):
            for key, value in data_row.items():
                data_row[key] = value.strip()
            data_row["line"] = idx + 2
            data_row["errors"] = {}

            error_dict = data_row["errors"]

            data_category = data_row["Category"]
            try:
                ImportMapper.map_category(data_category)
            except KeyError:
                error_dict["Category"] = tdt(
                    f"Category: {data_category} is not valid"
                )

            data_topic = data_row["Topic"]
            try:
                ImportMapper.map_topic(data_topic)
            except KeyError:
                error_dict["Topic"] = tdt(f"Topic: {data_topic} is not valid")

            data_data_quality = data_row["Data_Quality"]
            try:
                ImportMapper.map_data_quality(data_data_quality)
            except KeyError:
                error_dict["Data_Quality"] = tdt(
                    f"Data Quality: {data_data_quality} is not valid"
                )

            data_reason_for_null = data_row["Reason_for_Null_Data"]
            try:
                ImportMapper.map_reason_for_null(data_reason_for_null)
            except KeyError:
                error_dict["Reason_for_Null_Data"] = tdt(
                    f"Reason for Null Data: {data_reason_for_null} is not valid"
                )

            data_value_units = data_row["Value_Units"]
            try:
                ImportMapper.map_value_unit(data_value_units)
            except KeyError:
                error_dict["Value_Units"] = tdt(
                    f"Value Units: {data_value_units} is not valid"
                )

            data_value_displayed = data_row["Value_Displayed"]
            try:
                ImportMapper.map_value_displayed(data_value_displayed)
            except KeyError:
                error_dict["Value_Displayed"] = tdt(
                    f"Value displayed: {data_value_displayed} is not valid"
                )

            data_dimension_type = data_row["Dimension_Type"]
            try:
                ImportMapper.map_dimension_type(data_dimension_type)
            except KeyError:
                error_dict["Dimension_Type"] = tdt(
                    f"Dimension Type: {data_dimension_type} is not valid"
                )

            if data_dimension_type != "Age Group":
                data_dimension_value = data_row["Dimension_Value"]

                try:
                    ImportMapper.map_dimension_value(
                        (data_dimension_type, data_dimension_value)
                    )
                except KeyError:
                    error_dict["Dimension_Value"] = tdt(
                        f"Combination of Dimension Type: {data_dimension_type} and Dimension Value: {data_dimension_value} is not valid"
                    )

            data_period = data_row["Period"]
            try:
                ImportMapper.map_period(data_period)
            except KeyError:
                error_dict["Period"] = tdt(
                    f"Period: {data_period} is not valid"
                )

            data_arrow_flag = data_row["Arrow_Flag"]
            try:
                ImportMapper.map_arrow_flag(data_arrow_flag)
            except KeyError:
                error_dict["Arrow_Flag"] = tdt(
                    f"Arrow Flag: {data_arrow_flag} is not valid"
                )

            # value errors for open fields
            data_value = data_row["Value"]
            data_value_units = data_row["Value_Units"]
            if data_value != "":
                try:
                    float(data_value)
                except ValueError:
                    error_dict["Value"] = tdt(
                        f"Value: {data_value} is not a valid number"
                    )
                if error_dict.get("Value_Units") is None:
                    try:
                        mapped_value_unit = ImportMapper.map_value_unit(
                            data_value_units
                        )

                        err = IndDataCleaner.clean_value_data(
                            data_value,
                            mapped_value_unit,
                        )
                        if err:
                            error_dict["Value"] = str(err)
                    except KeyError:
                        error_dict["Value_Units"] = str(err)

            data_value_lower = data_row["Value_LowerCI"]
            if data_value_lower != "":
                try:
                    float(data_value_lower)
                except ValueError:
                    error_dict["Value_LowerCI"] = tdt(
                        f"Value LowerCI: {data_value_lower} is not a valid number"
                    )
                err = IndDataCleaner.clean_value_lower_data(
                    data_value, data_value_lower
                )
                if err:
                    error_dict["Value_LowerCI"] = str(err)

            data_value_upper = data_row["Value_UpperCI"]
            if data_value_upper != "":
                try:
                    float(data_value_upper)
                except ValueError:
                    error_dict["Value_UpperCI"] = tdt(
                        f"Value UpperCI: {data_row['Value_UpperCI']} is not a valid number"
                    )
                err = IndDataCleaner.clean_value_upper_data(
                    data_value, data_value_upper
                )
                if err:
                    error_dict["Value_UpperCI"] = str(err)

            data_single_year_timeframe = data_row["SingleYear_TimeFrame"]
            if data_single_year_timeframe != "":
                err = IndDataCleaner.clean_single_year_data(
                    data_single_year_timeframe
                )
                if err:
                    error_dict["SingleYear_TimeFrame"] = str(err)

            data_multi_year_timeframe = data_row["MultiYear_TimeFrame"]
            if data_multi_year_timeframe != "":
                err = IndDataCleaner.clean_multi_year_data(
                    data_multi_year_timeframe
                )
                if err:
                    error_dict["MultiYear_TimeFrame"] = str(err)

            # checking if indicator already exists
            data_indicator = data_row["Indicator"]
            data_detailed_indicator = data_row["Detailed Indicator"]
            data_sub_indicator = data_row["Sub_Indicator_Measurement"]
            try:
                indicator_obj = Indicator.objects.filter(
                    name=data_indicator,
                    category=ImportMapper.map_category(data_category),
                    topic=ImportMapper.map_topic(data_topic),
                    detailed_indicator=data_detailed_indicator,
                    sub_indicator_measurement=data_sub_indicator,
                ).first()
            except Exception:
                indicator_obj = None

            data_row["new_indicator"] = (
                True if indicator_obj is None else False
            )

            if indicator_obj is None and not test_rule(
                "can_create_indicator", self.user
            ):
                error_dict["Indicator"] = tdt(
                    f"Indicator: {data_indicator} does not exist and you do not have permission to create it"
                )

            if indicator_obj is not None and not test_rule(
                "can_access_indicator", self.user, indicator_obj
            ):
                error_dict["Indicator"] = tdt(
                    f"You do not have permission to edit data for Indicator: {indicator_obj.name}"
                )

            if "Period" not in error_dict and "Indicator" not in error_dict:
                period_obj = ImportMapper.map_period(data_period)

                if indicator_obj is not None and not test_rule(
                    "can_edit_indicator_data",
                    self.user,
                    {"indicator": indicator_obj, "period": period_obj},
                ):
                    error_dict["Period"] = tdt(
                        f"You do not have permission to edit data for period: {data_row['Period']}. Period is not current"
                    )

            data_dict.append(data_row)

        if errorlist:
            raise forms.ValidationError(mark_safe(" </br> ".join(errorlist)))

        return data_dict


class UploadIndicator(MustPassAuthCheckMixin, FormView):
    template_name = "indicators/upload/upload_indicator.jinja2"
    form_class = UploadForm

    def check_rule(self):
        return test_rule(
            "can_use_indicator_upload",
            self.request.user,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mapper"] = mapping_util
        return context

    def get_success_url(self):
        # return reverse("user_scoped_changelog", args=[self.request.user.id])
        return reverse("preview_upload")

    def form_valid(self, form):
        form.save()
        # messages.success(self.request, tdt("Data Uploaded Successfully"))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, tm("upload_error_msg"))
        return super().form_invalid(form)


class PreviewUpload(MustPassAuthCheckMixin, TemplateView):
    template_name = "indicators/upload/preview_upload.jinja2"

    def check_rule(self):
        return test_rule(
            "can_use_indicator_upload",
            self.request.user,
        )

    def get_context_data(self, **kwargs: Any):
        csv_data = self.request.session["upload_data"]
        from collections import defaultdict

        no_errors = True
        indicator_grouped_data = defaultdict(list)

        for datum in csv_data:
            # global error check across all data
            if datum["errors"]:
                no_errors = False
            # grouping data by indicator, detailed indicator, sub indicator measurement, category, topic
            indicator_grouped_data[
                datum["Indicator"],
                datum["Detailed Indicator"],
                datum["Sub_Indicator_Measurement"],
                datum["Category"],
                datum["Topic"],
            ].append(datum)

        context = {
            **super().get_context_data(**kwargs),
            "csv_data": csv_data,
            "grouped_data": indicator_grouped_data,
            "no_errors": no_errors,
        }
        return context


class SaveUpload(MustPassAuthCheckMixin, View):
    def check_rule(self):
        return test_rule(
            "can_use_indicator_upload",
            self.request.user,
        )

    def handle_indicator_save(self, datum):
        # try to find if indicator with same exact attributes exists first
        indicator_obj = Indicator.objects.filter(
            name=datum["Indicator"],
            category=ImportMapper.map_category(datum["Category"]),
            topic=ImportMapper.map_topic(datum["Topic"]),
            detailed_indicator=datum["Detailed Indicator"],
            sub_indicator_measurement=datum["Sub_Indicator_Measurement"],
        ).first()

        if indicator_obj is None:
            if test_rule("can_create_indicator", self.request.user):
                indicator_obj = Indicator.objects.create(
                    name=datum["Indicator"],
                    category=ImportMapper.map_category(datum["Category"]),
                    topic=ImportMapper.map_topic(datum["Topic"]),
                    detailed_indicator=datum["Detailed Indicator"],
                    sub_indicator_measurement=datum[
                        "Sub_Indicator_Measurement"
                    ],
                )
                indicator_obj.relevant_dimensions.set(
                    DimensionType.objects.all()
                )

        return indicator_obj

    def handle_indicator_data_save(self, indicator_obj, datum):
        period_val = ImportMapper.map_period(datum["Period"])

        if not test_rule(
            "can_access_indicator", self.request.user, indicator_obj
        ):
            return None

        dim_val = None
        lit_dim_val = None
        if datum["Dimension_Type"] != "Age Group":
            dim_val = ImportMapper.map_dimension_value(
                (datum["Dimension_Type"], datum["Dimension_Value"])
            )
        else:
            lit_dim_val = datum["Dimension_Value"]
        # filter data with all attributes equal to datum
        # to see if exact match exists
        indData_obj = IndicatorDatum.active_objects.filter(
            indicator=indicator_obj,
            dimension_type=ImportMapper.map_dimension_type(
                datum["Dimension_Type"]
            ),
            dimension_value=dim_val,
            literal_dimension_val=lit_dim_val,
            period=period_val,
            data_quality=ImportMapper.map_data_quality(datum["Data_Quality"]),
            arrow_flag=ImportMapper.map_arrow_flag(datum["Arrow_Flag"]),
            reason_for_null=ImportMapper.map_reason_for_null(
                datum["Reason_for_Null_Data"]
            ),
            value=(float(datum["Value"]) if datum["Value"] != "" else None),
            value_lower_bound=(
                float(datum["Value_LowerCI"])
                if datum["Value_LowerCI"] != ""
                else None
            ),
            value_upper_bound=(
                float(datum["Value_UpperCI"])
                if datum["Value_UpperCI"] != ""
                else None
            ),
            value_unit=ImportMapper.map_value_unit(datum["Value_Units"]),
            value_displayed=ImportMapper.map_value_displayed(
                datum["Value_Displayed"]
            ),
            single_year_timeframe=datum["SingleYear_TimeFrame"],
            multi_year_timeframe=datum["MultiYear_TimeFrame"],
        ).first()
        # if exact match exists, do nothing
        # if exact match does not exist, check if the data is modified
        # if data is modified, update data
        # if data is new, create new data
        if indData_obj is None:
            indData_obj, created = IndicatorDatum.active_objects.get_or_create(
                indicator=indicator_obj,
                dimension_type=ImportMapper.map_dimension_type(
                    datum["Dimension_Type"]
                ),
                dimension_value=dim_val,
                period=period_val,
                literal_dimension_val=lit_dim_val,
            )
            indData_obj.data_quality = ImportMapper.map_data_quality(
                datum["Data_Quality"]
            )
            indData_obj.reason_for_null = ImportMapper.map_reason_for_null(
                datum["Reason_for_Null_Data"]
            )
            indData_obj.value = (
                float(datum["Value"]) if datum["Value"] != "" else None
            )
            indData_obj.value_lower_bound = (
                float(datum["Value_LowerCI"])
                if datum["Value_LowerCI"] != ""
                else None
            )
            indData_obj.value_upper_bound = (
                float(datum["Value_UpperCI"])
                if datum["Value_UpperCI"] != ""
                else None
            )
            indData_obj.value_unit = ImportMapper.map_value_unit(
                datum["Value_Units"]
            )
            indData_obj.value_displayed = ImportMapper.map_value_displayed(
                datum["Value_Displayed"]
            )
            indData_obj.single_year_timeframe = datum["SingleYear_TimeFrame"]
            indData_obj.multi_year_timeframe = datum["MultiYear_TimeFrame"]
            indData_obj.save()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = request.session["upload_data"]
        for datum in data:
            indicator_obj = self.handle_indicator_save(datum)
            if indicator_obj is None:
                continue
            self.handle_indicator_data_save(indicator_obj, datum)

        messages.success(request, tdt("Data Uploaded Successfully"))
        response = HttpResponse()
        response["HX-Redirect"] = reverse(
            "user_scoped_changelog", args=[request.user.id]
        )
        return response
