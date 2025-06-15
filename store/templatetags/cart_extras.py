from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except:
        return ''


@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))
