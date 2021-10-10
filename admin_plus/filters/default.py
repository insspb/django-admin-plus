"""Contains overwrite for default Django filters with as dict resolution support."""
__all__ = [
    "DictFilter",
    "RelatedFieldListDictFilter",
    "BooleanFieldListDictFilter",
    "ChoicesFieldListDictFilter",
    "DateFieldListDictFilter",
    "AllValuesFieldListDictFilter",
    "RelatedOnlyFieldListDictFilter",
    "EmptyFieldListDictFilter",
    "SimpleListDictFilter",
    "SimpleDropdownDictFilter",
    "DropdownDictFilter",
    "ChoiceDropdownDictFilter",
    "RelatedDropdownDictFilter",
    "RelatedOnlyDropdownDictFilter",
    "BooleanDropdownDictFilter",
]
import logging
from typing import Any, Optional, Tuple

from admin_plus.settings import DEFAULT_ADMIN_FILTERS_GROUP
from django.contrib.admin import filters
from django.contrib.admin.options import IncorrectLookupParameters

logger = logging.getLogger(__name__)


class DictFilter(object):
    """ListFilter class extension with functions to work on dict basis."""

    update_before_filtering = False
    queryset_filter = False
    filter_group = DEFAULT_ADMIN_FILTERS_GROUP

    def get_filter_dict(self, request, queryset) -> Optional[Tuple[dict, int, Any]]:
        """
        Forms a Tuple for filter queryset generation.

        Expected tuple format: filters_dict, filters_group, filter_spec
        """
        return self.used_parameters, self.filter_group, self

    def qs_update_before_filtering(self, request, queryset):
        """Hook for queryset modification before filtering. (Like annotations)."""
        return queryset


class DropDownMixin(object):
    """Template for dropdown use in fields."""

    template = "admin/filter_dropdown.html"


class RelatedFieldListDictFilter(DictFilter, filters.RelatedFieldListFilter):
    """Base RelatedFieldListFilter overwrite with filtering by single query."""

    pass


class BooleanFieldListDictFilter(DictFilter, filters.BooleanFieldListFilter):
    """Base BooleanFieldListFilter overwrite with filtering by single query."""

    pass


class ChoicesFieldListDictFilter(DictFilter, filters.ChoicesFieldListFilter):
    """Base ChoicesFieldListFilter overwrite with filtering by single query."""

    pass


class DateFieldListDictFilter(DictFilter, filters.DateFieldListFilter):
    """Base DateFieldListFilter overwrite with filtering by single query."""

    pass


class AllValuesFieldListDictFilter(DictFilter, filters.AllValuesFieldListFilter):
    """Base AllValuesFieldListFilter overwrite with filtering by single query."""

    pass


class RelatedOnlyFieldListDictFilter(DictFilter, filters.RelatedOnlyFieldListFilter):
    """Base RelatedOnlyFieldListFilter overwrite with filtering by single query."""

    pass


class EmptyFieldListDictFilter(DictFilter, filters.EmptyFieldListFilter):
    """Base EmptyFieldListFilter overwrite with filtering by single query."""

    def get_filter_dict(self, request, queryset) -> Optional[Tuple[dict, int, Any]]:
        """
        Forms a Tuple for filter queryset generation.

        Expected tuple format: filters_dict, filters_group, filter_spec
        """
        if self.lookup_kwarg not in self.used_parameters:
            return None
        if self.lookup_val not in ("0", "1"):
            raise IncorrectLookupParameters

        lookup_condition = dict()
        if self.field.empty_strings_allowed:
            lookup_condition = {self.field_path: ""}
        if self.field.null:
            lookup_condition.update({"%s__isnull" % self.field_path: True})

        if self.lookup_val == "1":
            return lookup_condition, 0, self
        else:
            return {"%s__isnull" % self.field_path: False}, self.filter_group, self


class SimpleListDictFilter(DictFilter, filters.SimpleListFilter):
    """Base SimpleListFilter overwrite with filtering by single query."""

    pass


class SimpleDropdownDictFilter(DropDownMixin, SimpleListDictFilter):
    """Pre-defined Dropdown Filter for filters with queryset annotation requirement."""

    pass


class DropdownDictFilter(DropDownMixin, AllValuesFieldListDictFilter):
    """Dropdown Filter with on fly choices compilation."""

    pass


class ChoiceDropdownDictFilter(DropDownMixin, ChoicesFieldListDictFilter):
    """Dropdown Filter for fields with pre-defined choices (no queries)."""

    pass


class RelatedDropdownDictFilter(DropDownMixin, RelatedFieldListDictFilter):
    """Dropdown for Related Fields Filtering."""

    pass


class RelatedOnlyDropdownDictFilter(DropDownMixin, RelatedOnlyFieldListDictFilter):
    """
    RelatedOnlyFieldListFilter Dropdown replacement.

    Check docs: https://docs.djangoproject.com/en/dev/ref/contrib/admin/
    """

    pass


class BooleanDropdownDictFilter(DropDownMixin, BooleanFieldListDictFilter):
    """Boolean Field as Dropdown Filter with pre-defined values. Nulls supported."""

    pass
