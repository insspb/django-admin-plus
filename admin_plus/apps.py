"""Application registration for filter overwrite."""
from django.apps import AppConfig

from .settings import REPLACE_BASE_FILTERS, USE_DROPDOWNS_AS_DEFAULT


class AdminPlusConfig(AppConfig):
    """Floor Stack application initialization."""

    name = "admin_plus"
    verbose_name = "Admin Plus"

    def ready(self):
        """Launch post project initialization tasks."""

        if REPLACE_BASE_FILTERS:
            self.register_filters()

    def register_filters(self):
        """Do registration of modules that require complete application init."""
        from django.contrib.admin import FieldListFilter
        from django.db import models

        from .filters import (
            AllValuesFieldListDictFilter,
            BooleanDropdownDictFilter,
            BooleanFieldListDictFilter,
            ChoiceDropdownDictFilter,
            ChoicesFieldListDictFilter,
            DateRangeDictFilter,
            DateTimeRangeDictFilter,
            DropdownDictFilter,
            RangeNumericDictFilter,
            RelatedDropdownDictFilter,
            RelatedFieldListDictFilter,
        )

        # Declaration order matters! First use fields that do not make queries.
        FieldListFilter.register(
            lambda f: isinstance(
                f,
                (
                    models.AutoField,
                    models.IntegerField,
                    models.DecimalField,
                    models.FloatField,
                ),
            ),
            RangeNumericDictFilter,
            take_priority=True,
        )
        FieldListFilter.register(
            lambda f: isinstance(f, models.DateField),
            DateRangeDictFilter,
            take_priority=True,
        )
        FieldListFilter.register(
            lambda f: isinstance(f, models.DateTimeField),
            DateTimeRangeDictFilter,
            take_priority=True,
        )
        if USE_DROPDOWNS_AS_DEFAULT:
            FieldListFilter.register(
                lambda f: isinstance(f, models.BooleanField),
                BooleanDropdownDictFilter,
                take_priority=True,
            )
            FieldListFilter.register(
                lambda f: bool(f.choices),
                ChoiceDropdownDictFilter,
                take_priority=True,
            )
            FieldListFilter.register(
                lambda f: f.remote_field,
                RelatedDropdownDictFilter,
                take_priority=True,
            )
            FieldListFilter.register(
                lambda f: True,
                DropdownDictFilter,
                take_priority=True,
            )
        else:
            FieldListFilter.register(
                lambda f: isinstance(f, models.BooleanField),
                BooleanFieldListDictFilter,
                take_priority=True,
            )
            FieldListFilter.register(
                lambda f: bool(f.choices),
                ChoicesFieldListDictFilter,
                take_priority=True,
            )
            FieldListFilter.register(
                lambda f: f.remote_field,
                RelatedFieldListDictFilter,
                take_priority=True,
            )
            FieldListFilter.register(
                lambda f: True,
                AllValuesFieldListDictFilter,
                take_priority=True,
            )
