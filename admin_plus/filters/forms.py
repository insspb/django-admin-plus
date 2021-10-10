from django import forms
from django.utils.translation import ugettext_lazy as _


class SingleNumericForm(forms.Form):
    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name")
        super().__init__(*args, **kwargs)

        self.fields[name] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(attrs={"placeholder": _("Value")}),
        )


class RangeNumericForm(forms.Form):
    name = None

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop("name")
        super().__init__(*args, **kwargs)

        self.fields[self.name + "_gte"] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(attrs={"placeholder": _("From")}),
        )
        self.fields[self.name + "_lte"] = forms.FloatField(
            label="",
            required=False,
            widget=forms.NumberInput(attrs={"placeholder": _("To")}),
        )


class SliderNumericForm(RangeNumericForm):
    pass
