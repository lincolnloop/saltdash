import json
from urllib.parse import urlencode

from django.template import Library
from django.utils.safestring import mark_safe

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


@register.filter
def pretty_time(ms):
    """Convert milliseconds to more readable time"""
    if ms > 60000:
        min = int(ms / 60000)
        ms = ms - min * 60000
        return '{}:{:05.2f} min'.format(min, ms/1000)
    if ms > 1000:
        return '{:.2f} sec'.format(ms/1000)
    # pad one character right to keep alignment in states
    return mark_safe('{:.0f} ms&nbsp;'.format(round(ms, 0)))
