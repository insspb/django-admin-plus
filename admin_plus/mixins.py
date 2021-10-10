"""Mixins to extend django.contrib.admin.ModelAdmin functional."""
__all__ = [
    "AdminFieldsTwoStringMixin",
    "AllowPrefilterQueryMixin",
    "ChangeListDictFiltersMixin",
    "NumericFilterModelAdminMixin",
    "ModelAdminPlus",
]

from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect

from .views import ChangeListDictFilters


class AdminFieldsTwoStringMixin(metaclass=forms.MediaDefiningClass):
    """Allow multi-string columns names in admin table."""

    class Media:
        css = {"all": ("css/admin-extra.css",)}
        extend = True


class NumericFilterModelAdminMixin(metaclass=forms.MediaDefiningClass):
    class Media:
        css = {
            "all": (
                "js/nouislider.min.css",
                "css/admin-numeric-filter.css",
            )
        }
        js = (
            "js/wNumb.min.js",
            "js/nouislider.min.js",
            "js/admin-numeric-filter.js",
        )
        extend = True


class AllowPrefilterQueryMixin(object):
    """Extend changelist view with default filtering compatibility."""

    default_filter = dict()

    def changelist_view(self, request, extra_context=None):
        """Make pre-selection in admin panels and reflect them in query string."""
        if self.default_filter:
            default_filter = True
            query_string: str = request.META.get("QUERY_STRING", "")
            referer: str = request.META.get("HTTP_REFERER", "")

            if query_string or referer.startswith(request.build_absolute_uri()):
                default_filter = False

            if default_filter:
                current_get_dict = request.GET.copy()
                current_get_dict.update(self.default_filter)
                request.GET = current_get_dict
                return HttpResponseRedirect(f"{request.path}?{request.GET.urlencode()}")

        return super().changelist_view(request, extra_context=extra_context)


class ChangeListDictFiltersMixin(object):
    """Replaces base ChangeList class with ChangeList with DictFilters support."""

    def get_changelist(self, *args, **kwargs):
        """Returns updated ChangeList class for further processing in ModelAdmin."""
        return ChangeListDictFilters


class ModelAdminPlus(
    AllowPrefilterQueryMixin,
    ChangeListDictFiltersMixin,
    AdminFieldsTwoStringMixin,
    NumericFilterModelAdminMixin,
    admin.ModelAdmin,
):
    """
    Responsible for defining mandatory admin panel class settings for filters.

    Includes: New filters support and all default css/js files for them.
    """

    show_full_result_count = False
