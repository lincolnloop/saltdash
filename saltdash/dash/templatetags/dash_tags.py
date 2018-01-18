import json

from django.template import Library

from ..models import Result

register = Library()


@register.filter
def pretty_json(dict_val):
    return json.dumps(dict_val, indent=2)


@register.simple_tag
def get_minions():
    return (Result.objects.order_by('minion')
                          .values_list('minion', flat=True)
                          .distinct())
