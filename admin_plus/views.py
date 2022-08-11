"""Some django.contrib.admin.views views generate functions/classes overwrite."""
import logging
from copy import deepcopy
from typing import Any, Tuple

from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.db.models import Exists, OuterRef

from .settings import DEFAULT_ADMIN_FILTERS_GROUP

logger = logging.getLogger(__name__)


class ChangeListDictFilters(ChangeList):
    """
    ChangeList overwrite with filters as dict support.

    Fully compatible with old style filters.
    """

    def apply_filters_and_annotations(self, filters_and_annotations, request, queryset):
        """Compile queryset with ordered filters and annotations."""
        ordered_filters = self.order_filters_groups(filters_and_annotations)
        _applied_qs_filters = 0
        qs = queryset
        logger.debug("total filters groups: %s.", len(ordered_filters))

        for filters_dict in ordered_filters:
            filters = filters_dict["filters"]
            need_qs_mod = filters_dict["need_qs_mod"]
            qs_only_filters = filters_dict["qs_only_filters"]
            logger.debug("Group has %s qs modification filters.", len(need_qs_mod))
            logger.debug("Group has %s qs only filters.", len(qs_only_filters))

            for f_spec in need_qs_mod:
                qs = f_spec.qs_update_before_filtering(request, qs)

            # May be empty for complex queryset only filter groups
            if filters:
                logger.debug("Group applied dict filters: %s", filters)
                qs = qs.filter(**filters)

            # This is compatible part with old filters or queryset only filters
            for f_spec in qs_only_filters:
                new_qs = f_spec.queryset(request, qs)
                if new_qs is not None:
                    _applied_qs_filters += 1
                    qs = new_qs

            logger.debug("Group has %s applied qs only filters.", _applied_qs_filters)

        return qs

    def get_filters_and_annotations(self, request, queryset):
        """Form filters_and_annotations list from new style and old style filters."""
        # Tuple inside:
        # filters_dict, filters_group, filter_spec
        filters_and_annotations: list[Tuple[dict, bool, Any]] = []
        qs = queryset

        for filter_spec in self.filter_specs:
            try:
                filters_and_annotations.append(filter_spec.get_filter_dict(request, qs))
            except AttributeError:
                # Old filters compatibility
                filters_group = DEFAULT_ADMIN_FILTERS_GROUP
                filter_spec.queryset_filter = True
                filters_and_annotations.append(({}, filters_group, filter_spec))

        return filters_and_annotations

    def get_filtered_queryset(self, request):
        """
        Form a queryset with minimum amount of joins.

        Old custom filters are applied first.
        """
        qs = self.root_queryset
        filters_and_annotations = self.get_filters_and_annotations(request, qs)

        qs = self.apply_filters_and_annotations(filters_and_annotations, request, qs)

        return qs

    def order_filters_groups(self, filters_and_annotations):
        """Combine results from filters groups and order groups output."""
        filters = {}
        group_dict_default = {"filters": {}, "need_qs_mod": [], "qs_only_filters": []}

        for value in filters_and_annotations:
            if not value:
                continue
            f_dict, f_group, f_spec = value
            group_dict = filters.setdefault(f_group, deepcopy(group_dict_default))
            group_dict["filters"].update(f_dict)

            if getattr(f_spec, "update_before_filtering", False):
                group_dict["need_qs_mod"].append(f_spec)

            if getattr(f_spec, "queryset_filter", False):
                group_dict["qs_only_filters"].append(f_spec)

        return [v for k, v in sorted(filters.items(), key=lambda item: item[0])]

    def get_queryset(self, request):
        """Overwrite of original 'get_queryset' with debugging info."""
        # First, we collect all the declared list filters.
        (
            self.filter_specs,
            self.has_filters,
            remaining_lookup_params,
            filters_may_have_duplicates,
            self.has_active_filters,
        ) = self.get_filters(request)

        # Then, we let every list filter modify the queryset to its liking.
        qs = self.get_filtered_queryset(request)

        try:
            # Finally, we apply the remaining lookup parameters from the query
            # string (i.e. those that haven't already been processed by the
            # filters).
            qs = qs.filter(**remaining_lookup_params)
        except (SuspiciousOperation, ImproperlyConfigured):
            # Allow certain types of errors to be re-raised as-is so that the
            # caller can treat them in a special way.
            raise
        except Exception as e:
            # Every other error is caught with a naked except, because we don't
            # have any other way of validating lookup parameters. They might be
            # invalid if the keyword arguments are incorrect, or if the values
            # are not in the correct type, so we might get FieldError,
            # ValueError, ValidationError, or ?.
            raise IncorrectLookupParameters(e)

        # Apply search results
        qs, search_may_have_duplicates = self.model_admin.get_search_results(
            request,
            qs,
            self.query,
        )

        # Set query string for clearing all filters.
        self.clear_all_filters_qs = self.get_query_string(
            new_params=remaining_lookup_params,
            remove=self.get_filters_params(),
        )
        # Remove duplicates from results, if necessary
        if filters_may_have_duplicates | search_may_have_duplicates:
            qs = qs.filter(pk=OuterRef("pk"))
            qs = self.root_queryset.filter(Exists(qs))

        # Set ordering.
        ordering = self.get_ordering(request, qs)
        qs = qs.order_by(*ordering)

        if not qs.query.select_related:
            qs = self.apply_select_related(qs)

        return qs
