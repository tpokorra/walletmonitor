from django import template

register = template.Library()

@register.filter
def formatcurrency(value):
    if value > 100:
        return "%0.0f" % (value,)
    return "%0.2f" % (value,)

