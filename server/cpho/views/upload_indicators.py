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

from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
    Period,
)
from cpho.text import tdt, tm

from .view_util import MustPassAuthCheckMixin, upload_mapper


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
        mapper = upload_mapper()
        # checking for invalid values in the csv
        for idx, data_row in enumerate(reader):
            for key, value in data_row.items():
                data_row[key] = value.strip()
            data_row["line"] = idx + 2
            data_row["errors"] = {}
            if data_row["Category"] not in mapper["category_mapper"]:
                data_row["errors"]["Category"] = tdt(
                    f"Category: {data_row['Category']} is not valid"
                )
            if data_row["Topic"] not in mapper["topic_mapper"]:
                data_row["errors"]["Topic"] = tdt(
                    tdt(f"Topic: {data_row['Topic']} is not valid")
                )
            if data_row["Data_Quality"] not in mapper["data_quality_mapper"]:
                data_row["errors"]["Data_Quality"] = tdt(
                    f"Data quality: {data_row['Data_Quality']} is not valid"
                )
            if (
                data_row["Reason_for_Null_Data"]
                not in mapper["reason_for_null_mapper"]
            ):
                data_row["errors"]["Reason_for_Null_Data"] = tdt(
                    f"Reason_for_Null_Data: {data_row['Reason_for_Null_Data']} is not valid"
                )
            if data_row["Value_Units"] not in mapper["value_unit_mapper"]:
                data_row["errors"]["Value_Units"] = tdt(
                    f"Value Units: {data_row['Value_Units']} is not valid"
                )
            if (
                data_row["Value_Displayed"]
                not in mapper["value_displayed_mapper"]
            ):
                data_row["errors"]["Value_Displayed"] = tdt(
                    f"Value displayed: {data_row['Value_Displayed']} is not valid"
                )
            if data_row["Dimension_Type"] != "Age Group":
                if (
                    data_row["Dimension_Type"]
                    not in mapper["dimension_type_mapper"]
                ):
                    data_row["errors"]["Dimension_Type"] = tdt(
                        f"Dimension Type: {data_row['Dimension_Type']} is not valid"
                    )
                if (
                    data_row["Dimension_Type"],
                    data_row["Dimension_Value"],
                ) not in mapper["non_literal_dimension_value_mapper"]:
                    data_row["errors"]["Dimension_Value"] = tdt(
                        f"Combination of Dimension Type: {data_row['Dimension_Type']} and Dimension Value: {data_row['Dimension_Value']} is not valid"
                    )
            if data_row["Period"] not in mapper["period_mapper"]:
                data_row["errors"]["Period"] = tdt(
                    f"Period: {data_row['Period']} is not valid"
                )
            if data_row["Arrow_Flag"] not in mapper["arrow_flag_mapper"]:
                data_row["errors"]["Arrow_Flag"] = tdt(
                    f"Arrow Flag: {data_row['Arrow_Flag']} is not valid"
                )

            # checking if indicator already exists
            try:
                indicator_obj = Indicator.objects.filter(
                    name=data_row["Indicator"],
                    category=mapper["category_mapper"][data_row["Category"]],
                    topic=mapper["topic_mapper"][data_row["Topic"]],
                    detailed_indicator=data_row["Detailed Indicator"],
                    sub_indicator_measurement=data_row[
                        "Sub_Indicator_Measurement"
                    ],
                ).first()
            except Exception:
                indicator_obj = None

            data_row["new_indicator"] = (
                True if indicator_obj is None else False
            )

            if indicator_obj is None and not test_rule(
                "can_create_indicator", self.user
            ):
                data_row["errors"]["Indicator"] = tdt(
                    f"Indicator: {data_row['Indicator']} does not exist and you do not have permission to create it"
                )

            if indicator_obj is not None and not test_rule(
                "can_access_indicator", self.user, indicator_obj
            ):
                data_row["errors"]["Indicator"] = tdt(
                    f"You do not have permission to edit data for Indicator: {indicator_obj.name}"
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
        context["mapper"] = upload_mapper()
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
                print(datum["errors"])
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
        mapper = upload_mapper()
        # try to find if indicator with same exact attributes exists first
        indicator_obj = Indicator.objects.filter(
            name=datum["Indicator"],
            category=mapper["category_mapper"][datum["Category"]],
            topic=mapper["topic_mapper"][datum["Topic"]],
            detailed_indicator=datum["Detailed Indicator"],
            sub_indicator_measurement=datum["Sub_Indicator_Measurement"],
        ).first()

        if indicator_obj is None:
            if test_rule("can_create_indicator", self.request.user):
                indicator_obj = Indicator.objects.create(
                    name=datum["Indicator"],
                    category=mapper["category_mapper"][datum["Category"]],
                    topic=mapper["topic_mapper"][datum["Topic"]],
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
        mapper = upload_mapper()

        period_val = mapper["period_mapper"][datum["Period"]]

        if not test_rule(
            "can_access_indicator", self.request.user, indicator_obj
        ):
            return None

        dim_val = None
        lit_dim_val = None
        if datum["Dimension_Type"] != "Age Group":
            dim_val = mapper["non_literal_dimension_value_mapper"][
                (datum["Dimension_Type"], datum["Dimension_Value"])
            ]
        else:
            lit_dim_val = datum["Dimension_Value"]
        # filter data with all attributes equal to datum
        # to see if exact match exists
        indData_obj = IndicatorDatum.active_objects.filter(
            indicator=indicator_obj,
            dimension_type=mapper["dimension_type_mapper"][
                datum["Dimension_Type"]
            ],
            dimension_value=dim_val,
            literal_dimension_val=lit_dim_val,
            period=period_val,
            data_quality=mapper["data_quality_mapper"][datum["Data_Quality"]],
            arrow_flag=mapper["arrow_flag_mapper"][datum["Arrow_Flag"]],
            reason_for_null=mapper["reason_for_null_mapper"][
                datum["Reason_for_Null_Data"]
            ],
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
            value_unit=mapper["value_unit_mapper"][datum["Value_Units"]],
            value_displayed=mapper["value_displayed_mapper"][
                datum["Value_Displayed"]
            ],
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
                dimension_type=mapper["dimension_type_mapper"][
                    datum["Dimension_Type"]
                ],
                dimension_value=dim_val,
                period=period_val,
                literal_dimension_val=lit_dim_val,
            )
            indData_obj.data_quality = mapper["data_quality_mapper"][
                datum["Data_Quality"]
            ]
            indData_obj.reason_for_null = mapper["reason_for_null_mapper"][
                datum["Reason_for_Null_Data"]
            ]
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
            indData_obj.value_unit = mapper["value_unit_mapper"][
                datum["Value_Units"]
            ]
            indData_obj.value_displayed = mapper["value_displayed_mapper"][
                datum["Value_Displayed"]
            ]
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
