from django import forms

from cpho.text import tm as _

widget_classes_that_should_have_form_control = [
    forms.widgets.TextInput,
    forms.widgets.NumberInput,
    forms.widgets.DateInput,
    forms.widgets.DateTimeInput,
    forms.widgets.TimeInput,
    forms.widgets.Select,
    forms.widgets.SelectMultiple,
    forms.widgets.EmailInput,
    forms.widgets.URLInput,
    forms.widgets.PasswordInput,
    forms.widgets.FileInput,
    forms.widgets.Textarea,
]


class FormControlMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # not all forms have a class Meta

        for key, field in self.fields.items():
            for widget_class in widget_classes_that_should_have_form_control:
                if isinstance(field.widget, widget_class):
                    field.widget.attrs["class"] = (
                        field.widget.attrs.get("class", "") + " form-control"
                    )


class NumberInputMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.NumberInput):
                field.widget.attrs["type"] = "number"
                # right-align numbers
                field.widget.attrs["class"] = (
                    field.widget.attrs.get("class", "") + " text-end"
                )


class TallTextAreasMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.Textarea):
                field.widget.attrs["rows"] = 5


class M2MWidgetMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, field in self.fields.items():
            if isinstance(field.widget, forms.SelectMultiple):
                field.widget = forms.CheckboxSelectMultiple(
                    choices=field.choices
                )


class DateInputMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, field in self.fields.items():
            if isinstance(field.widget, forms.widgets.DateInput):
                field.widget.input_type = "date"


class YesNoMixin(forms.Form):
    """
    Translates/capitalizes the default yes/no labels
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if hasattr(field, "choices") and isinstance(field.choices, list):
                self.translate_choices(field.choices)

            if hasattr(field.widget, "choices") and isinstance(
                field.choices, list
            ):
                self.translate_choices(field.widget.choices)

    @staticmethod
    def translate_choices(choices):
        # modifies a list in place

        for i, (value, label) in enumerate(choices):
            if label in ("yes", "Yes"):
                choices[i] = (value, _("yes"))
            elif label in ("no", "No"):
                choices[i] = (value, _("no"))


class DescribedByErrorMixin(forms.Form):
    """
    adds aria-describedby attributes for error messages
    assumes error messages follow the field naming convention
    """

    def error_id_for_field(self, bound_field):
        id_for_label = bound_field.id_for_label
        error_id = f"{id_for_label}_errormessage"
        return error_id

    def full_clean(self):
        r = super().full_clean()
        for bound_field in self.visible_fields():
            if self.errors.get(bound_field.name):
                error_id = self.error_id_for_field(bound_field)
                widget = bound_field.field.widget
                current_aria_describedby = widget.attrs.get(
                    "aria-describedby", ""
                )
                widget.attrs["aria-describedby"] = (
                    current_aria_describedby + " " + error_id
                )

        return r


class StandardFormMixin(
    FormControlMixin,
    NumberInputMixin,
    TallTextAreasMixin,
    M2MWidgetMixin,
    DateInputMixin,
    YesNoMixin,
):
    required_css_class = "required"
