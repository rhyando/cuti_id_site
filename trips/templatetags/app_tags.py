from django import template
from django.conf import settings
import re

numeric_test = re.compile("^\d+$")
register = template.Library()

@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg

@register.filter(name='subtract_days')
def subtract(value, arg):
    return (value - arg).days

@register.filter
def to_class_name(value):
    return value.__class__.__name__

@register.filter
def to_field_name(value):
    return value._meta.fields[1:]

@register.filter
def getattribute(value, arg):
    """Gets an attribute of an object dynamically from a string name"""
    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key') and value.has_key(arg):
        return value[arg]
    elif numeric_test.match(str(arg)) and len(value) > int(arg):
        return value[int(arg)]
    else:
        return settings.TEMPLATE_STRING_IF_INVALID

