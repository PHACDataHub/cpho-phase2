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

from cpho.models import (
    DimensionType,
    DimensionValue,
    Indicator,
    IndicatorDatum,
    Period,
)
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

    # def deduce_dimension_type(self, record, csv_line_number):
    #     dimension_deduced_bool = False
    #     dimension_deduced = None
    #     dimension_col_name = None

    #     checking_column = "Geography"
    #     geography = record[checking_column]
    #     if geography and geography.lower() not in [
    #         "canada",
    #         "null",
    #         "nan",
    #         "",
    #     ]:
    #         # print("DIMESNION: ", geography, " FOR: ", record, "\n")
    #         dimension_deduced_bool = True
    #         dimension_deduced = geography
    #         dimension_col_name = checking_column

    #     checking_column = "Sex"
    #     sex = record[checking_column]
    #     if sex and sex.lower() not in ["both sexes", "null", "nan", ""]:
    #         # print("DIMESNION: ", sex, " FOR: ", record, "\n")
    #         if dimension_deduced_bool:
    #             print(
    #                 "WARNING ON LINE (",
    #                 csv_line_number,
    #                 "): DIMENSION ALREADY DEDUCED ",
    #                 dimension_deduced,
    #                 "\nNEW DIMENSION FOUND: ",
    #                 sex,
    #                 "\nPLEASE CHECK RECORD: ",
    #                 record,
    #             )
    #             return None
    #         else:
    #             dimension_deduced_bool = True
    #             dimension_deduced = sex
    #             dimension_col_name = checking_column

    #     checking_column = "Gender"
    #     gender = record[checking_column]
    #     if gender and gender.lower() not in [
    #         "both genders",
    #         "null",
    #         "nan",
    #         "",
    #     ]:
    #         # print("DIMESNION: ", gender, " FOR: ", record, "\n")
    #         if dimension_deduced_bool:
    #             print(
    #                 "WARNING ON LINE (",
    #                 csv_line_number,
    #                 "): DIMENSION ALREADY DEDUCED ",
    #                 dimension_deduced,
    #                 "\nNEW DIMENSION FOUND: ",
    #                 gender,
    #                 "\nPLEASE CHECK RECORD: ",
    #                 record,
    #             )
    #             return None
    #         else:
    #             dimension_deduced_bool = True
    #             dimension_deduced = gender
    #             dimension_col_name = checking_column

    #     checking_column = "Age_Group"
    #     age_group = record[checking_column]
    #     if age_group and age_group.lower() not in ["null", "nan", ""]:
    #         # print("DIMESNION: ", age_group, " FOR: ", record, "\n")
    #         if dimension_deduced_bool:
    #             print(
    #                 "WARNING ON LINE (",
    #                 csv_line_number,
    #                 "): DIMENSION ALREADY DEDUCED ",
    #                 dimension_deduced,
    #                 "\nNEW DIMENSION FOUND: ",
    #                 age_group,
    #                 "\nPLEASE CHECK RECORD: ",
    #                 record,
    #             )
    #             return None
    #         else:
    #             dimension_deduced_bool = True
    #             dimension_deduced = age_group
    #             dimension_col_name = checking_column

    #     checking_column = "Geography"
    #     if not dimension_deduced_bool and geography.lower() == "canada":
    #         # print("DIMESNION: ", geography, " FOR: ", record, "\n")
    #         if dimension_deduced_bool:
    #             print(
    #                 "WARNING ON LINE (",
    #                 csv_line_number,
    #                 "): DIMENSION ALREADY DEDUCED ",
    #                 dimension_deduced,
    #                 "\nNEW DIMENSION FOUND: ",
    #                 geography,
    #                 "\nPLEASE CHECK RECORD: ",
    #                 record,
    #             )
    #             return None
    #         else:
    #             dimension_deduced_bool = True
    #             dimension_deduced = geography
    #             dimension_col_name = checking_column

    #     if not dimension_deduced_bool:
    #         print(
    #             "WARNING ON LINE (",
    #             csv_line_number,
    #             "): DIMENSION NOT FOUND ",
    #             "\nPLEASE CHECK RECORD: ",
    #             record,
    #         )
    #         return None
    #     return {
    #         "dimension_col_name": dimension_col_name,
    #         "dimension_value": dimension_deduced,
    #     }

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

            # data_dimension = self.deduce_dimension_type(data_row, idx)
            # print(data_dimension)
            data_dict.append(data_row)

        return data_dict


class UploadIndicator(FormView):
    template_name = "indicators/upload_indicator.jinja2"
    form_class = UploadForm

    def get_success_url(self):
        return reverse("list_indicators")

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            data = form.cleaned_data["csv_file"]
            # print(data)
            category_mapper = {
                "": "",
                "FACTORS INFLUENCING HEALTH": "factors_influencing_health",
                "GENERAL HEALTH STATUS": "general_health_status",
                "HEALTH OUTCOMES": "health_outcomes",
            }

            subcategory_mapper = {
                "": "",
                "SOCIAL FACTORS": "social_factors",
                "HEALTH STATUS": "health_status",
                "COMMUNICABLE DISEASES": "communicable_diseases",
                "SUBSTANCE USE": "substance_use",
                "CHILDHOOD AND FAMILY FACTORS": "childhood_and_family_risk_and_protective_factors",
                "CHILDHOOD AND FAMILY RISK FACTORS": "childhood_and_family_risk_and_protective_factors",
                "CHRONIC DISEASES AND MENTAL HEALTH": "chronic_diseases_and_mental_health",
            }

            data_quality_mapper = {
                "": "",
                "CAUTION": "caution",
                "GOOD": "good",
                "ACCEPTABLE": "acceptable",
                "SUPPRESSED": "suppressed",
                "VERY GOOD": "excellent",
            }
            value_unit_mapper = {
                "": "",
                "%": "%",
                "PER 100,000": "per_100k",
                "YEARS": "years",
                "PER 1,000 CENSUS INHABITANTS": "per_100k_census",
                "PER 10,000 PATIENT DAYS": "per_100k_patient_days",
                "PER 100,000 LIVE BIRTHS": "per_100k_live_births",
            }

            dimension_type_mapper = {
                "Province": DimensionType.objects.get(code="province"),
                "Age Group": DimensionType.objects.get(code="age"),
                "Sex": DimensionType.objects.get(code="sex"),
                "Canada": DimensionType.objects.get(code="canada"),
                "Region": DimensionType.objects.get(code="region"),
                "Gender": DimensionType.objects.get(code="gender"),
            }

            non_literal_dimension_value_mapper = {
                "Province_ON": DimensionValue.objects.get(
                    dimension_type__code="province", value="on"
                ),
                "Province_AB": DimensionValue.objects.get(
                    dimension_type__code="province", value="ab"
                ),
                "Province_SK": DimensionValue.objects.get(
                    dimension_type__code="province", value="sk"
                ),
                "Province_MB": DimensionValue.objects.get(
                    dimension_type__code="province", value="mb"
                ),
                "Province_BC": DimensionValue.objects.get(
                    dimension_type__code="province", value="bc"
                ),
                "Province_QC": DimensionValue.objects.get(
                    dimension_type__code="province", value="qc"
                ),
                "Province_NB": DimensionValue.objects.get(
                    dimension_type__code="province", value="nb"
                ),
                "Province_NS": DimensionValue.objects.get(
                    dimension_type__code="province", value="ns"
                ),
                "Province_NL": DimensionValue.objects.get(
                    dimension_type__code="province", value="nl"
                ),
                "Province_PE": DimensionValue.objects.get(
                    dimension_type__code="province", value="pe"
                ),
                "Province_NU": DimensionValue.objects.get(
                    dimension_type__code="province", value="nu"
                ),
                "Province_NT": DimensionValue.objects.get(
                    dimension_type__code="province", value="nt"
                ),
                "Province_YT": DimensionValue.objects.get(
                    dimension_type__code="province", value="yt"
                ),
                "Region_ATLANTIC": DimensionValue.objects.get(
                    dimension_type__code="region", value="atlantic"
                ),
                "Region_PRAIRIE": DimensionValue.objects.get(
                    dimension_type__code="region", value="prairies"
                ),
                "Region_TERRITORIES": DimensionValue.objects.get(
                    dimension_type__code="region", value="territories"
                ),
                "Gender_MEN": DimensionValue.objects.get(
                    dimension_type__code="gender", value="men"
                ),
                "Gender_WOMEN": DimensionValue.objects.get(
                    dimension_type__code="gender", value="women"
                ),
                "Gender_BOYS": DimensionValue.objects.get(
                    dimension_type__code="gender", value="boys"
                ),
                "Gender_GIRLS": DimensionValue.objects.get(
                    dimension_type__code="gender", value="girls"
                ),
                "Sex_MALES": DimensionValue.objects.get(
                    dimension_type__code="sex", value="m"
                ),
                "Sex_FEMALES": DimensionValue.objects.get(
                    dimension_type__code="sex", value="f"
                ),
                "Canada_CANADA": DimensionValue.objects.get(
                    dimension_type__code="canada", value="canada"
                ),
            }
            # TODO: Update Periods
            preiod_val = Period.objects.get(year="2023")
            for datum in data:
                print(datum)
                print("\n\n")
                indicator_obj, ind_created = Indicator.objects.get_or_create(
                    name=datum["Indicator"],
                    detailed_indicator=datum["Detailed Indicator"],
                    sub_indicator_measurement=datum[
                        "Sub_Indicator_Measurement"
                    ],
                    category=category_mapper[datum["Category"]],
                    sub_category=subcategory_mapper[datum["Topic"]],
                )

                dim_val = None
                lit_dim_val = None
                if datum["Dimension_Type"] != "Age Group":
                    dim_val = non_literal_dimension_value_mapper[
                        f'{datum["Dimension_Type"]}_{datum["Dimension_Value"]}'
                    ]
                else:
                    lit_dim_val = datum["Dimension_Value"]

                indData_obj, id_created = IndicatorDatum.objects.get_or_create(
                    indicator=indicator_obj,
                    dimension_type=dimension_type_mapper[
                        datum["Dimension_Type"]
                    ],
                    dimension_value=dim_val,
                    literal_dimension_val=lit_dim_val,
                    period=preiod_val,
                    data_quality=data_quality_mapper[datum["Data_Quality"]],
                    value=float(datum["Value"])
                    if datum["Value"] != ""
                    else None,
                    value_lower_bound=float(datum["Value_LowerCI"])
                    if datum["Value_LowerCI"] != ""
                    else None,
                    value_upper_bound=float(datum["Value_UpperCI"])
                    if datum["Value_UpperCI"] != ""
                    else None,
                    value_unit=value_unit_mapper[datum["Value_Displayed"]],
                    single_year_timeframe=datum["SingleYear_TimeFrame"],
                    multi_year_timeframe=datum["MultiYear_TimeFrame"],
                )

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
