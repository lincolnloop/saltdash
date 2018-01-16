import json

from django.template import Library

register = Library()


@register.filter
def pretty_json(dict_val):
    return json.dumps(dict_val, indent=2)
