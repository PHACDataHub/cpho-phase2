import csv
import time

from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import FormView

from server.rules_framework import test_rule

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
        super(UploadForm, self).__init__(*args, **kwargs)

    csv_file = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    def handle_indicators(self, datum):
        mapper = upload_mapper()
        # try to find if indicator with same exact attributes exists first
        indicator_obj = Indicator.objects.filter(
            name=datum["Indicator"],
            category=mapper["category_mapper"][datum["Category"]],
            sub_category=mapper["subcategory_mapper"][datum["Topic"]],
            detailed_indicator=datum["Detailed Indicator"],
            sub_indicator_measurement=datum["Sub_Indicator_Measurement"],
        )

        if len(indicator_obj) == 0 and test_rule(
            "can_create_indicator", self.user
        ):
            indicator_obj = Indicator.objects.create(
                name=datum["Indicator"],
                category=mapper["category_mapper"][datum["Category"]],
                sub_category=mapper["subcategory_mapper"][datum["Topic"]],
                detailed_indicator=datum["Detailed Indicator"],
                sub_indicator_measurement=datum["Sub_Indicator_Measurement"],
            )
        elif len(indicator_obj) == 0 and not test_rule(
            "can_create_indicator", self.user
        ):
            self.add_error(
                None,
                tdt(
                    f"Indicator: {datum['Indicator']} does not exist and you do not have permission to create it"
                ),
            )
            indicator_obj = None
        else:
            indicator_obj = indicator_obj[0]

        return indicator_obj

    def handle_indicator_data(self, indicator_obj, datum):
        mapper = upload_mapper()
        preiod_val = Period.objects.get(
            year=2021, quarter=None, year_type="calendar"
        )

        if not test_rule("can_edit_indicator_data", self.user, indicator_obj):
            self.add_error(
                None,
                tdt(
                    f"You do not have permission to edit data for Indicator: {indicator_obj.name}"
                ),
            )
            return None

        dim_val = None
        lit_dim_val = None
        if datum["Dimension_Type"] != "Age Group":
            dim_val = mapper["non_literal_dimension_value_mapper"][
                (datum["Dimension_Type"], datum["Dimension_Value"])
            ]
        else:
            lit_dim_val = datum["Dimension_Value"]

        indData_obj = IndicatorDatum.objects.filter(
            indicator=indicator_obj,
            dimension_type=mapper["dimension_type_mapper"][
                datum["Dimension_Type"]
            ],
            dimension_value=dim_val,
            literal_dimension_val=lit_dim_val,
            period=preiod_val,
            data_quality=mapper["data_quality_mapper"][datum["Data_Quality"]],
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
            value_unit=mapper["value_unit_mapper"][datum["Value_Displayed"]],
            single_year_timeframe=datum["SingleYear_TimeFrame"],
            multi_year_timeframe=datum["MultiYear_TimeFrame"],
        )

        if len(indData_obj) == 0:
            print("Editing Indicator Data")
            indData_obj, created = IndicatorDatum.objects.get_or_create(
                indicator=indicator_obj,
                dimension_type=mapper["dimension_type_mapper"][
                    datum["Dimension_Type"]
                ],
                dimension_value=dim_val,
                literal_dimension_val=lit_dim_val,
            )
            indData_obj.period = preiod_val
            indData_obj.data_quality = mapper["data_quality_mapper"][
                datum["Data_Quality"]
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
                datum["Value_Displayed"]
            ]
            indData_obj.single_year_timeframe = datum["SingleYear_TimeFrame"]
            indData_obj.multi_year_timeframe = datum["MultiYear_TimeFrame"]
            indData_obj.save()

        else:
            print("Indicator data already exists")

    def save(self):
        data = self.cleaned_data["csv_file"]
        for datum in data:
            indicator_obj = self.handle_indicators(datum)

            if indicator_obj is None:
                continue

            self.handle_indicator_data(indicator_obj, datum)

    def clean_csv_file(self):
        start_time = time.time()

        csv_file = self.cleaned_data["csv_file"]
        if not csv_file.name.endswith(".csv"):
            raise forms.ValidationError(tdt("File is not CSV type"))
        if csv_file.multiple_chunks():
            raise forms.ValidationError(
                tdt("Uploaded file is too big. Maximum size allowed is 2 MB")
            )
        file_data = csv_file.read().decode("utf-8-sig").splitlines()
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
            # "COUNTRY",
            # "Geography",
            # "Sex",
            # "Gender",
            # "Age_Group",
            # "Age_Group_Type",
            # "Living_Arrangement",
            # "PT_Data_Availability",
            # "Value_Units",
        ]
        missing_headers = []
        for header in required_headers:
            if header not in reader.fieldnames:
                missing_headers.append(header)
        if missing_headers:
            raise forms.ValidationError(
                tdt("File is missing the required columns: ")
                + ", ".join(missing_headers)
            )

        errorlist = []
        mapper = upload_mapper()
        for idx, data_row in enumerate(reader):
            for key, value in data_row.items():
                data_row[key] = value.strip()
            if data_row["Category"] not in mapper["category_mapper"]:
                errorlist.append(
                    tdt(
                        f"row: {idx} Category: {data_row['Category']} is not valid"
                    )
                )
            if data_row["Topic"] not in mapper["subcategory_mapper"]:
                errorlist.append(
                    tdt(
                        f"row: {idx} Sub category: {data_row['Topic']} is not valid"
                    )
                )
            if data_row["Data_Quality"] not in mapper["data_quality_mapper"]:
                errorlist.append(
                    tdt(
                        f"row: {idx} Data quality: {data_row['Data_Quality']} is not valid"
                    )
                )
            if data_row["Value_Displayed"] not in mapper["value_unit_mapper"]:
                errorlist.append(
                    tdt(
                        f"row: {idx} Value displayed: {data_row['Value_Displayed']} is not valid"
                    )
                )
            if data_row["Dimension_Type"] != "Age Group":
                if (
                    data_row["Dimension_Type"]
                    not in mapper["dimension_type_mapper"]
                ):
                    errorlist.append(
                        tdt(
                            f"row: {idx} Dimension Type: {data_row['Dimension_Type']} is not valid"
                        )
                    )
                if (
                    data_row["Dimension_Type"],
                    data_row["Dimension_Value"],
                ) not in mapper["non_literal_dimension_value_mapper"]:
                    errorlist.append(
                        tdt(
                            f"row: {idx} Combination of Dimension Type: {data_row['Dimension_Type']} and Dimension Value: {data_row['Dimension_Value']} is not valid"
                        )
                    )

            # data_dimension = deduce_dimension_type(data_row, idx)
            # print(data_dimension)
            data_dict.append(data_row)

        if errorlist:
            raise forms.ValidationError(mark_safe(" </br> ".join(errorlist)))

        print("--- %s seconds ---" % (time.time() - start_time))

        return data_dict


class UploadIndicator(MustPassAuthCheckMixin, FormView):
    template_name = "indicators/upload_indicator.jinja2"
    form_class = UploadForm

    def check_rule(self):
        return test_rule(
            "can_upload_indicator",
            self.request.user,
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("list_indicators")

    def form_valid(self, form):
        start_time = time.time()
        form.save()
        print("--- %s seconds ---" % (time.time() - start_time))
        messages.success(self.request, tdt("Data Uploaded Successfully"))
        return super().form_valid(form)

    def form_invalid(self, form):
        try:
            messages.error(
                self.request,
                tdt(
                    "There was an error uploading the file. Please correct the errors below and try again"
                ),
            )
        except Exception:
            messages.error(
                self.request,
                tdt("There was an error uploading the file. Please try again"),
            )
        return super().form_invalid(form)
