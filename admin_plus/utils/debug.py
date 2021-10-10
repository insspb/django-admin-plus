"""Django additional handy utilities."""
__all__ = ["pretty_sql", "print_pretty_sql"]
import sqlparse


def pretty_sql(queryset, **opt):
    """Convert queryset query to readable format."""
    return sqlparse.format(str(queryset.query), reindent=True, indent_width=4, **opt)


def print_pretty_sql(queryset, **opt):
    """Prints formatted sql to console output."""
    print(pretty_sql(queryset, **opt))
