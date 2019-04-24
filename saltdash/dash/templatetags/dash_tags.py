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
    return Result.objects.order_by("minion").values_list("minion", flat=True).distinct()


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Replace a single GET parameter while maintaining others"""
    query = context["request"].GET.dict()
    query.update(kwargs)
    return urlencode(query)


@register.filter
def pretty_time(ms):
    """Convert milliseconds to more readable time"""
    if ms > 60000:
        min = int(ms / 60000)
        ms = ms - min * 60000
        return "{}:{:05.2f} min".format(min, ms / 1000)
    if ms > 1000:
        return "{:.2f} sec".format(ms / 1000)
    # pad one character right to keep alignment in states
    return mark_safe("{:.0f} ms&nbsp;".format(round(ms, 0)))


@register.filter
def clipped_page_range(page_range: range, current_page: int) -> list:
    """Abbreviated page range to avoid a massive pagination"""
    page_range = list(page_range)
    if len(page_range) <= 8:
        return page_range
    # show first two and last two pages
    start = page_range[:2]
    end = page_range[-2:]

    # prevent middle from going beyond start/end
    if current_page >= start[0] + 2:
        first_middle = current_page - 2
    else:
        first_middle = start[0]
    if current_page <= end[-1] - 2:
        last_middle = current_page + 2
    else:
        last_middle = end[-1]
    middle = list(range(first_middle, last_middle + 1))

    # add gaps in pages as None if necessary
    if middle[0] > start[-1] + 1:
        pages = start + [None] + middle
    else:
        pages = list(set(start + middle))
    if middle[-1] + 1 > end[0]:
        for p in end:
            if pages[-1] < p:
                pages.append(p)
    else:
        pages = pages + [None] + end
    return pages
