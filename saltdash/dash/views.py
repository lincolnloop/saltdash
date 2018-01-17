from django.conf import settings
from django.core.paginator import Paginator, Page, InvalidPage
from django.db.models import QuerySet
from django.http import (HttpResponseRedirect, Http404,
                         HttpResponsePermanentRedirect, HttpRequest)
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Job, Result

ITEMS_PER_PAGE = 25


def paginate_queryset(queryset: QuerySet, request: HttpRequest) -> dict:
    """Paginate the queryset, if needed."""
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page') or 1
    try:
        page_number = int(page)
    except ValueError:
        if page == 'last':
            page_number = paginator.num_pages
        else:
            raise Http404(
                "Page is not 'last', nor can it be converted to an int.")
    try:
        page = paginator.page(page_number)
        return {
            'paginator': paginator,
            'page_obj': page,
            'object_list': page.object_list,
            'is_paginated': page.has_other_pages(),
        }
    except InvalidPage as e:
        raise Http404(f'Invalid page ({page_number}): {str(e)}')


def get_started(request):
    template = 'dash/get_started.html'
    print(settings.DATABASES['default'])
    context = {
        'host': settings.DATABASES['default']['HOST'] or 'localhost',
        'name': settings.DATABASES['default']['NAME'],
        'port': settings.DATABASES['default']['PORT'] or 5432,
        'user': settings.DATABASES['default']['USER'] or None,
    }
    return render(request, template, context)


def job_list(request):
    template = "dash/job_list.html"
    qs = Job.objects.all()
    show_system = 'system' in request.GET
    if not show_system:
        qs = qs.exclude(load__fun='saltutil.find_job')
    context = {
        'job_list': qs,
        'has_system_jobs': show_system,
    }
    context.update(paginate_queryset(qs, request))
    return render(request, template, context)


def job_detail(request, jid, success=None):
    template = "dash/job_detail.html"
    job = get_object_or_404(Job, jid=jid)
    filters = {'jid': jid}
    if success is not None:
        filters['success'] = success
    qs = Result.objects.filter(**filters)
    count = qs.count()
    if count == 1:
        return HttpResponseRedirect(
            reverse('dash:result_detail', kwargs={'pk': qs[0].pk}))
    if count == 0:
        raise Http404
    context = {
        'job': job,
        'result_list': qs,
    }
    context.update(paginate_queryset(qs, request))
    return render(request, template, context)


def job_result_for_minion(request, jid,minion):
    template = "dash/job_detail.html"
    result = get_object_or_404(Result, jid=jid, id=minion)
    return HttpResponsePermanentRedirect(result.get_absolute_url())


def result_list(request):
    template = "dash/result_list.html"
    qs = Result.objects.all()
    show_system = 'system' in request.GET
    if not show_system:
        qs = qs.exclude(fun='saltutil.find_job')
    context = {
        'result_list': qs,
        'has_system_jobs': show_system,
    }
    context.update(paginate_queryset(qs, request))
    return render(request, template, context)


def result_detail(request, pk):
    template = "dash/result_detail.html"
    ret = get_object_or_404(Result, pk=pk)
    context = {
        'job': ret.job,
        'result': ret,
    }
    return render(request, template, context)
