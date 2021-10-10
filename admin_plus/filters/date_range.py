"""
Customization of filters from django-admin-rangefilter package.

Original package: https://github.com/silentsokolov/django-admin-rangefilter

Compatibility with Django < 3 removed.
"""
__all__ = ["DateRangeDictFilter", "DateTimeRangeDictFilter"]
try:
    import pytz
except ImportError:
    pytz = None

import datetime

from django import forms
from django.conf import settings
from django.contrib.admin.filters import FieldListFilter
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.admin.widgets import AdminSplitDateTime as BaseAdminSplitDateTime
from django.template.defaultfilters import slugify
from django.templatetags.static import StaticNode
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .default import DictFilter


class OnceCallMedia(object):
    _is_rendered = False

    def __str__(self):
        return str([str(s) for s in self._js])

    def __repr__(self):
        return "OnceCallMedia(js=%r)" % ([str(s) for s in self._js])

    def __call__(self):
        if self._is_rendered:
            return []

        self._is_rendered = True
        return self._js

    @property
    def _js(self):
        return [
            StaticNode.handle_simple("admin/js/calendar.js"),
            StaticNode.handle_simple("admin/js/admin/DateTimeShortcuts.js"),
        ]


class AdminSplitDateTime(BaseAdminSplitDateTime):
    def format_output(self, rendered_widgets):
        return format_html(
            '<p class="datetime">{}</p><p class="datetime rangetime">{}</p>',
            rendered_widgets[0],
            rendered_widgets[1],
        )


class DateRangeFilter(FieldListFilter):
    _request_key = "DJANGO_RANGEFILTER_ADMIN_JS_LIST"

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg_gte = f"{field_path}__range__gte"
        self.lookup_kwarg_lte = f"{field_path}__range__lte"

        self.default_gte, self.default_lte = self._get_default_values(
            request, model_admin, field_path
        )

        super().__init__(field, request, params, model, model_admin, field_path)
        self.request = request
        self.model_admin = model_admin
        self.form = self.get_form(request)

        custom_title = self._get_custom_title(request, model_admin, field_path)
        if custom_title:
            self.title = custom_title

    def get_timezone(self, request):
        return timezone.get_default_timezone()

    @staticmethod
    def _get_custom_title(request, model_admin, field_path):
        title_method_name = f"get_rangefilter_{field_path}_title"
        title_method = getattr(model_admin, title_method_name, None)

        if callable(title_method):
            return title_method(request, field_path)

    @staticmethod
    def _get_default_values(request, model_admin, field_path):
        default_method_name = f"get_rangefilter_{field_path}_default"
        default_method = getattr(model_admin, default_method_name, None)

        if callable(default_method):
            return default_method(request)

        return None, None

    @staticmethod
    def make_dt_aware(value, timezone):
        if settings.USE_TZ and pytz is not None:
            default_tz = timezone
            if value.tzinfo is not None:
                value = default_tz.normalize(value)
            else:
                value = default_tz.localize(value)
        return value

    def choices(self, cl):
        yield {
            # slugify converts any non-unicode characters to empty characters
            # but system_name is required, if title converts to empty string use id
            # https://github.com/silentsokolov/django-admin-rangefilter/issues/18
            "system_name": force_str(
                slugify(self.title) if slugify(self.title) else id(self.title)
            ),
            "query_string": cl.get_query_string({}, remove=self._get_expected_fields()),
        }

    def expected_parameters(self):
        return self._get_expected_fields()

    def queryset(self, request, queryset):
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data:
                return queryset.filter(
                    **self._make_query_filter(request, validated_data)
                )
        return queryset

    def _get_expected_fields(self):
        return [self.lookup_kwarg_gte, self.lookup_kwarg_lte]

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
        date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)

        if date_value_gte:
            query_params[f"{self.field_path}__gte"] = self.make_dt_aware(
                datetime.datetime.combine(date_value_gte, datetime.time.min),
                self.get_timezone(request),
            )
        if date_value_lte:
            query_params[f"{self.field_path}__lte"] = self.make_dt_aware(
                datetime.datetime.combine(date_value_lte, datetime.time.max),
                self.get_timezone(request),
            )

        return query_params

    template = "admin/filter_date_range.html"

    def get_form(self, request):
        form_class = self._get_form_class()
        return form_class(self.used_parameters or None)

    def _get_form_class(self):
        fields = self._get_form_fields()

        form_class = type(
            str("DateRangeForm"), (forms.BaseForm,), {"base_fields": fields}
        )

        # lines below ensure that the js static files are loaded just once
        # even if there is more than one DateRangeFilter in use
        js_list = getattr(self.request, self._request_key, None)
        if not js_list:
            js_list = OnceCallMedia()
            setattr(self.request, self._request_key, js_list)

        form_class.js = js_list

        return form_class

    def _get_form_fields(self):
        return {
            self.lookup_kwarg_gte: forms.DateField(
                label="",
                widget=AdminDateWidget(attrs={"placeholder": _("From date")}),
                localize=True,
                required=False,
                initial=self.default_gte,
            ),
            self.lookup_kwarg_lte: forms.DateField(
                label="",
                widget=AdminDateWidget(attrs={"placeholder": _("To date")}),
                localize=True,
                required=False,
                initial=self.default_lte,
            ),
        }


class DateTimeRangeFilter(DateRangeFilter):
    def _get_expected_fields(self):
        return [
            f"{self.lookup_kwarg_gte}_0",
            f"{self.lookup_kwarg_gte}_1",
            f"{self.lookup_kwarg_lte}_0",
            f"{self.lookup_kwarg_lte}_1",
        ]

    def _get_form_fields(self):
        return {
            self.lookup_kwarg_gte: forms.SplitDateTimeField(
                label="",
                widget=AdminSplitDateTime(attrs={"placeholder": _("From date")}),
                localize=True,
                required=False,
                initial=self.default_gte,
            ),
            self.lookup_kwarg_lte: forms.SplitDateTimeField(
                label="",
                widget=AdminSplitDateTime(attrs={"placeholder": _("To date")}),
                localize=True,
                required=False,
                initial=self.default_lte,
            ),
        }

    def _make_query_filter(self, request, validated_data):
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
        date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)

        if date_value_gte:
            query_params[f"{self.field_path}__gte"] = self.make_dt_aware(
                date_value_gte, self.get_timezone(request)
            )
        if date_value_lte:
            query_params[f"{self.field_path}__lte"] = self.make_dt_aware(
                date_value_lte, self.get_timezone(request)
            )

        return query_params


class DateRangeModuleDictGeneration(DictFilter):
    """Base code generation for Date and DateTime Range filters."""

    def get_filter_dict(self, request, queryset):
        """
        Forms a Tuple for filter queryset generation.

        Expected tuple format: filters_dict, filters_group, filter_spec
        """
        if self.form.is_valid():
            validated_data = dict(self.form.cleaned_data.items())
            if validated_data:
                filters_dict = self._make_query_filter(request, validated_data)
                return filters_dict, self.filter_group, self

        return None


class DateRangeDictFilter(DateRangeModuleDictGeneration, DateRangeFilter):
    """Extension of DateRangeFilter class with filters as dictionary compatibility."""

    pass


class DateTimeRangeDictFilter(DateRangeModuleDictGeneration, DateTimeRangeFilter):
    """
    Extension of DateTimeRangeFilter class with filters as dictionary compatibility.
    """

    pass
