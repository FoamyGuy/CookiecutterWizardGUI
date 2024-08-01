from django import template

register = template.Library()

@register.filter
def get_type(value):
    return type(value)


@register.filter
def is_list(value):
    return isinstance(value, list)