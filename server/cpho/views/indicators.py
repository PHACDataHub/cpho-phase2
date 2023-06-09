from typing import Any

from django import forms
from django.contrib import messages
from django.forms.models import ModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)

from cpho.models import DimensionType, Indicator
from cpho.text import tdt, tm


class IndicatorForm(ModelForm):
    class Meta:
        model = Indicator
        fields = [
            "name",
            "category",
            "sub_category",
            "detailed_indicator",
            "sub_indicator_measurement",
        ]

    name = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    category = forms.ChoiceField(
        required=False,
        choices=Indicator.CATEGORY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    sub_category = forms.ChoiceField(
        required=False,
        choices=Indicator.SUB_CATEGORY_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )
    detailed_indicator = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    sub_indicator_measurement = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )


class UploadForm(forms.Form):
    csv_file = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
            }
        ),
    )


class ListIndicators(ListView):
    model = Indicator
    template_name = "indicators/list_indicators.jinja2"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }


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

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }


class EditIndicator(UpdateView):
    model = Indicator
    form_class = IndicatorForm
    template_name = "indicators/edit_indicator.jinja2"

    def get_success_url(self):
        return reverse("view_indicator", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
        }


class UploadIndicator(FormView):
    template_name = "indicators/upload_indicator.jinja2"
    form_class = UploadForm

    def get_success_url(self):
        return reverse("list_indicators")

    def deduce_dimension_type(self, record, csv_line_number):
        dimension_deduced_bool = False
        dimension_deduced = None
        dimension_col_name = None

        checking_column = "Geography"
        geography = record[checking_column]
        if geography and geography.lower() not in ["canada", "null", ""]:
            # print("DIMESNION: ", geography, " FOR: ", record, "\n")
            dimension_deduced_bool = True
            dimension_deduced = geography
            dimension_col_name = checking_column

        checking_column = "Sex"
        sex = record[checking_column]
        if sex and sex.lower() not in ["both sexes", "null", ""]:
            # print("DIMESNION: ", sex, " FOR: ", record, "\n")
            if dimension_deduced_bool:
                print(
                    "WARNING ON LINE (",
                    csv_line_number,
                    "): DIMENSION ALREADY DEDUCED ",
                    dimension_deduced,
                    "\nNEW DIMENSION FOUND: ",
                    sex,
                    "\nPLEASE CHECK RECORD: ",
                    record,
                )
                return None
            else:
                dimension_deduced_bool = True
                dimension_deduced = sex
                dimension_col_name = checking_column

        checking_column = "Gender"
        gender = record[checking_column]
        if gender and gender.lower() not in ["both genders", "null", ""]:
            # print("DIMESNION: ", gender, " FOR: ", record, "\n")
            if dimension_deduced_bool:
                print(
                    "WARNING ON LINE (",
                    csv_line_number,
                    "): DIMENSION ALREADY DEDUCED ",
                    dimension_deduced,
                    "\nNEW DIMENSION FOUND: ",
                    gender,
                    "\nPLEASE CHECK RECORD: ",
                    record,
                )
                return None
            else:
                dimension_deduced_bool = True
                dimension_deduced = gender
                dimension_col_name = checking_column

        checking_column = "Age_Group"
        age_group = record[checking_column]
        if age_group and age_group.lower() not in ["null", ""]:
            # print("DIMESNION: ", age_group, " FOR: ", record, "\n")
            if dimension_deduced_bool:
                print(
                    "WARNING ON LINE (",
                    csv_line_number,
                    "): DIMENSION ALREADY DEDUCED ",
                    dimension_deduced,
                    "\nNEW DIMENSION FOUND: ",
                    age_group,
                    "\nPLEASE CHECK RECORD: ",
                    record,
                )
                return None
            else:
                dimension_deduced_bool = True
                dimension_deduced = age_group
                dimension_col_name = checking_column

        checking_column = "Geography"
        if not dimension_deduced_bool and geography.lower() == "canada":
            # print("DIMESNION: ", geography, " FOR: ", record, "\n")
            if dimension_deduced_bool:
                print(
                    "WARNING ON LINE (",
                    csv_line_number,
                    "): DIMENSION ALREADY DEDUCED ",
                    dimension_deduced,
                    "\nNEW DIMENSION FOUND: ",
                    geography,
                    "\nPLEASE CHECK RECORD: ",
                    record,
                )
                return None
            else:
                dimension_deduced_bool = True
                dimension_deduced = geography
                dimension_col_name = checking_column

        if not dimension_deduced_bool:
            print(
                "WARNING ON LINE (",
                csv_line_number,
                "): DIMENSION NOT FOUND ",
                "\nPLEASE CHECK RECORD: ",
                record,
            )
            return None
        return {
            "dimension_col_name": dimension_col_name,
            "dimension_value": dimension_deduced,
        }

    def post(self, *args, **kwargs):
        print("post")
        try:
            csv_file = self.request.FILES["csv_file"]
            if not csv_file.name.endswith(".csv"):
                messages.error(self.request, tdt("File is not CSV type"))
                return HttpResponseRedirect(reverse("upload_indicator"))
            if csv_file.multiple_chunks():
                messages.error(
                    self.request,
                    tdt(
                        "Uploaded file is too big. Maximum size allowed is 2 MB"
                    ),
                )
                return HttpResponseRedirect(reverse("upload_indicator"))

            ### Dont remove this code; might need for custom parsing
            file_data = csv_file.read().decode("utf-8-sig")
            lines = file_data.split("\n")
            data_dict = []
            for idx, line in enumerate(lines):
                # print(line)
                fields = line.split(",")
                if idx == 0:
                    headers = [s.strip() for s in fields]
                    # TODO: check if headers are as expected
                else:
                    if len(fields) != len(headers):
                        continue
                    data_row = {}
                    for i, field in enumerate(fields):
                        data_row[headers[i]] = field.strip()
                    data_dimension = self.deduce_dimension_type(data_row, idx)
                    print(data_dimension)
                    data_dict.append(data_row)
                    # print("SUCCESSFULLY ADDED ROW: ", idx)
            # print(data_dict)
            messages.success(self.request, tdt("Data Uploaded Successfully"))

        except Exception as err:
            messages.error(
                self.request, tdt("Unable to upload file: ") + repr(err)
            )

        return HttpResponseRedirect(reverse("upload_indicator"))
