from decimal import Decimal

from django import template

from app_core.constants import MONTH_NAMES  # noqa: F401 — re-exported for templatetag use

register = template.Library()


@register.filter
def brl(value):
    """Format Decimal/float as Brazilian currency string: R$ 1.234,56"""
    try:
        value = Decimal(str(value))
        negative = value < 0
        abs_val = abs(value)
        # Format with 2 decimal places
        formatted = f'{abs_val:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
        prefix = '-R$ ' if negative else 'R$ '
        return f'{prefix}{formatted}'
    except Exception:
        return 'R$ 0,00'


@register.filter
def month_name(value):
    """Return the Portuguese month name for an integer 1-12."""
    try:
        return MONTH_NAMES[int(value)]
    except (KeyError, ValueError, TypeError):
        return ''


@register.filter
def balance_color(value):
    """Return CSS class based on whether balance is positive or negative."""
    try:
        return 'text-green-500' if Decimal(str(value)) >= 0 else 'text-red-500'
    except Exception:
        return 'text-gray-500'
