from django import template

register = template.Library()

@register.filter
def splitbycomma(value):
    """Splits a string by comma and trims whitespace from each item."""
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]
