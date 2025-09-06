from django import template

register = template.Library()

@register.filter
def monitorformatcurrency(value):
    if not value:
        return "0.00"
    if value > 100:
        return "%0.0f" % (value,)
    if value < 0.01:
        return "%0.5f" % (value,)
    if value < 0.1:
        return "%0.4f" % (value,)
    return "%0.2f" % (value,)

