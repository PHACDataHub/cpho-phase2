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

    def post(self, *args, **kwargs):
        print("post")
        try:
            csv_file = self.request.FILES["csv_file"]
            if not csv_file.name.endswith(".csv"):
                messages.error(self.request, "File is not CSV type")
                return HttpResponseRedirect(reverse("upload_indicator"))
            if csv_file.multiple_chunks():
                messages.error(
                    self.request,
                    "Uploaded file is too big. Maximum size allowed is 2 MB",
                )
                return HttpResponseRedirect(reverse("upload_indicator"))
            file_data = csv_file.read().decode("utf-8-sig")
            lines = file_data.split("\n")
            data_dict = []
            for idx, line in enumerate(lines):
                # print(line)
                fields = line.split(",")
                if idx == 0:
                    headers = [s.strip() for s in fields]
                else:
                    if len(fields) != len(headers):
                        continue
                    data_row = {}
                    for i, field in enumerate(fields):
                        data_row[headers[i]] = field.strip()
                    data_dict.append(data_row)
                    print("SUCCESSFULLY ADDED ROW: ", idx)
            print(data_dict)
            messages.success(self.request, "Data Uploaded ")

        except Exception as err:
            messages.error(self.request, "Unable to upload file. " + repr(err))

        return HttpResponseRedirect(reverse("upload_indicator"))
