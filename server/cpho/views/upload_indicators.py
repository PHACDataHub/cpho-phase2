import csv

from django import forms
from django.contrib import messages
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


class UploadForm(forms.Form):
    csv_file = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    def deduce_dimension_type(self, record, csv_line_number):
        dimension_deduced_bool = False
        dimension_deduced = None
        dimension_col_name = None

        checking_column = "Geography"
        geography = record[checking_column]
        if geography and geography.lower() not in [
            "canada",
            "null",
            "nan",
            "",
        ]:
            # print("DIMESNION: ", geography, " FOR: ", record, "\n")
            dimension_deduced_bool = True
            dimension_deduced = geography
            dimension_col_name = checking_column

        checking_column = "Sex"
        sex = record[checking_column]
        if sex and sex.lower() not in ["both sexes", "null", "nan", ""]:
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
        if gender and gender.lower() not in [
            "both genders",
            "null",
            "nan",
            "",
        ]:
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
        if age_group and age_group.lower() not in ["null", "nan", ""]:
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

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        if not csv_file.name.endswith(".csv"):
            raise forms.ValidationError(tdt("File is not CSV type"))
        if csv_file.multiple_chunks():
            raise forms.ValidationError(
                tdt("Uploaded file is too big. Maximum size allowed is 2 MB")
            )

        # ### Please dont remove this code; might need for custom parsing later
        # file_data = csv_file.read().decode("utf-8-sig")
        # lines = file_data.split("\n")
        # data_dict = []
        # for idx, line in enumerate(lines):
        #     # print(line)
        #     fields = line.split(",")
        #     if idx == 0:
        #         headers = [s.strip() for s in fields]
        #         # TODO: check if headers are as expected
        #     else:
        #         if len(fields) != len(headers):
        #             continue
        #         data_row = {}
        #         for i, field in enumerate(fields):
        #             data_row[headers[i]] = field.strip()
        #         data_dimension = self.deduce_dimension_type(data_row, idx)
        #         print(data_dimension)
        #         data_dict.append(data_row)
        #         # print("SUCCESSFULLY ADDED ROW: ", idx)
        # # print(data_dict)
        file_data = csv_file.read().decode("utf-8-sig").splitlines()
        # Not sure if this is needed in the future
        # file_data = [
        #     unicodedata.normalize("NFKD", line) for line in file_data
        # ]
        reader = csv.DictReader(file_data)
        data_dict = []
        for idx, data_row in enumerate(reader):
            # Very annoying that i have to do this; but gives me errors otherwise
            for key, value in data_row.items():
                data_row[key] = value.strip()
            data_dimension = self.deduce_dimension_type(data_row, idx)
            print(data_dimension)
            data_dict.append(data_row)

        return csv_file


class UploadIndicator(FormView):
    template_name = "indicators/upload_indicator.jinja2"
    form_class = UploadForm

    def get_success_url(self):
        return reverse("list_indicators")

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            messages.success(self.request, tdt("Data Uploaded Successfully"))
            return HttpResponseRedirect(self.get_success_url())
        else:
            try:
                messages.error(
                    self.request,
                    # need a smarter implementation for this
                    form.errors.as_data()["csv_file"][0].messages[0],
                )
            except Exception:
                messages.error(
                    self.request,
                    tdt(
                        "There was an error uploading the file. Please try again"
                    ),
                )
            return self.form_invalid(form)
