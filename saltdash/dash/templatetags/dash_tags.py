import json
from urllib.parse import urlencode

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


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Replace a single GET parameter while maintaining others"""
    query = context['request'].GET.dict()
    query.update(kwargs)
    return urlencode(query)
