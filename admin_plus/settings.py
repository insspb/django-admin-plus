"""Admin Plus Custom settings module."""
from django.conf import settings

DEFAULT_ADMIN_FILTERS_GROUP = getattr(settings, "AP_DEFAULT_ADMIN_FILTERS_GROUP", 99)
REPLACE_BASE_FILTERS = getattr(settings, "AP_REPLACE_BASE_FILTERS", True)
USE_DROPDOWNS_AS_DEFAULT = getattr(settings, "AP_USE_DROPDOWNS_AS_DEFAULT", True)
