"""
DecimalField, IntegerField, FloatField, AutoField fields range filters.

Original code repository: https://github.com/lukasvinclav/django-admin-numeric-filter
Original code author: Lukas Vinclav
"""
__all__ = [
    "SingleNumericDictFilter",
    "RangeNumericDictFilter",
    "RangeNumericSimpleDictFilter",
    "SliderNumericDictFilter",
]
from django.contrib import admin
from django.contrib.admin.utils import reverse_field_path
from django.db.models import Max, Min
from django.db.models.fields import AutoField, DecimalField, FloatField, IntegerField

from .default import DictFilter, SimpleListDictFilter
from .forms import RangeNumericForm, SingleNumericForm, SliderNumericForm


class BaseRangeDictFiler(DictFilter, admin.FieldListFilter):
    request = None
    parameter_name = None

    def __init__(self, field, request, params, model, model_admin, field_path):
        if not isinstance(field, (DecimalField, IntegerField, FloatField, AutoField)):
            raise TypeError(
                f"Class {type(self.field)} is not supported for {self.__class__.__name__}."
            )

        super().__init__(field, request, params, model, model_admin, field_path)
        self.request = request

        if self.parameter_name is None:
            self.parameter_name = self.field_path


class SingleNumericDictFilter(BaseRangeDictFiler):
    template = "admin/filter_numeric_single.html"

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        if self.parameter_name in params:
            value = params.pop(self.parameter_name)
            self.used_parameters[self.parameter_name] = value

    def get_filter_dict(self, request, queryset):
        if self.value():
            return {self.parameter_name: self.value()}, self.filter_group, self
        return None

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{self.parameter_name: self.value()})

    def value(self):
        return self.used_parameters.get(self.parameter_name, None)

    def expected_parameters(self):
        return [self.parameter_name]

    def choices(self, changelist):
        return (
            {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": SingleNumericForm(
                    name=self.parameter_name,
                    data={self.parameter_name: self.value()},
                ),
            },
        )


class RangeNumericDictFilterMixin(object):
    """Workflow of Range Filter. Used by different init methods."""

    template = "admin/filter_numeric_range.html"

    def _get_filter_dict(self, request, queryset):
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + "_gte", None)
        if value_from is not None and value_from != "":
            filters.update(
                {
                    self.parameter_name
                    + "__gte": self.used_parameters.get(
                        self.parameter_name + "_gte", None
                    ),
                }
            )

        value_to = self.used_parameters.get(self.parameter_name + "_lte", None)
        if value_to is not None and value_to != "":
            filters.update(
                {
                    self.parameter_name
                    + "__lte": self.used_parameters.get(
                        self.parameter_name + "_lte", None
                    ),
                }
            )
        return filters

    def get_filter_dict(self, request, queryset):
        filters_spec = self._get_filter_dict(request, queryset)
        if filters_spec:
            return filters_spec, self.filter_group, self

    def queryset(self, request, queryset):
        filters = self._get_filter_dict(request, queryset)

        return queryset.filter(**filters)

    def expected_parameters(self):
        return [f"{self.parameter_name}_lte", f"{self.parameter_name}_gte"]

    def choices(self, changelist):
        return (
            {
                "request": self.request,
                "parameter_name": self.parameter_name,
                "form": RangeNumericForm(
                    name=self.parameter_name,
                    data={
                        self.parameter_name
                        + "_gte": self.used_parameters.get(
                            self.parameter_name + "_gte", None
                        ),
                        self.parameter_name
                        + "_lte": self.used_parameters.get(
                            self.parameter_name + "_lte", None
                        ),
                    },
                ),
            },
        )


class RangeNumericDictFilter(RangeNumericDictFilterMixin, BaseRangeDictFiler):
    """Range Filter for normal list_filter definition."""

    def __init__(self, field, request, params, model, model_admin, field_path):
        """Init by FieldListFilter signature."""
        super().__init__(field, request, params, model, model_admin, field_path)
        if self.parameter_name + "_gte" in params:
            value = params.pop(self.parameter_name + "_gte")
            self.used_parameters[self.parameter_name + "_gte"] = value

        if self.parameter_name + "_lte" in params:
            value = params.pop(self.parameter_name + "_lte")
            self.used_parameters[self.parameter_name + "_lte"] = value


class RangeNumericSimpleDictFilter(RangeNumericDictFilterMixin, SimpleListDictFilter):
    """Range Filter for custom filters with annotations definition."""

    def __init__(self, request, params, model, model_admin):
        """Init by SimpleListDictFilter signature."""
        super().__init__(request, params, model, model_admin)

        self.request = request
        if self.parameter_name + "_gte" in params:
            value = params.pop(self.parameter_name + "_gte")
            self.used_parameters[self.parameter_name + "_gte"] = value

        if self.parameter_name + "_lte" in params:
            value = params.pop(self.parameter_name + "_lte")
            self.used_parameters[self.parameter_name + "_lte"] = value

    def has_output(self):
        """Base class required method overwrite with constant value."""
        return True

    def lookups(self, request, model_admin):
        """Base class required method overwrite with constant value."""
        return ()


class SliderNumericDictFilter(RangeNumericDictFilter):
    MAX_DECIMALS = 7
    STEP = None

    template = "admin/filter_numeric_slider.html"
    field = None

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        self.field = field
        parent_model, reverse_path = reverse_field_path(model, field_path)

        if model == parent_model:
            self.q = model_admin.get_queryset(request)
        else:
            self.q = parent_model._default_manager.all()

    def choices(self, changelist):
        total = self.q.all().count()

        min_value = self.q.all().aggregate(min=Min(self.parameter_name)).get("min", 0)

        if total > 1:
            max_value = (
                self.q.all().aggregate(max=Max(self.parameter_name)).get("max", 0)
            )
        else:
            max_value = None

        if isinstance(self.field, (FloatField, DecimalField)):
            decimals = self.MAX_DECIMALS
            step = self.STEP if self.STEP else self._get_min_step(self.MAX_DECIMALS)
        else:
            decimals = 0
            step = self.STEP if self.STEP else 1

        return (
            {
                "decimals": decimals,
                "step": step,
                "parameter_name": self.parameter_name,
                "request": self.request,
                "min": min_value,
                "max": max_value,
                "value_from": self.used_parameters.get(
                    self.parameter_name + "_gte", min_value
                ),
                "value_to": self.used_parameters.get(
                    self.parameter_name + "_lte", max_value
                ),
                "form": SliderNumericForm(
                    name=self.parameter_name,
                    data={
                        self.parameter_name
                        + "_gte": self.used_parameters.get(
                            self.parameter_name + "_gte", min_value
                        ),
                        self.parameter_name
                        + "_lte": self.used_parameters.get(
                            self.parameter_name + "_lte", max_value
                        ),
                    },
                ),
            },
        )

    def _get_min_step(self, precision):
        result_format = "{{:.{}f}}".format(precision - 1)
        return float(result_format.format(0) + "1")
