from django.http import (HttpResponseRedirect, Http404,
                         HttpResponsePermanentRedirect)
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import Job, Result


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
    return render(request, template, context)

def result_detail(request, pk):
    template = "dash/result_detail.html"
    ret = get_object_or_404(Result, pk=pk)
    context = {
        'job': ret.job,
        'result': ret,
    }
    return render(request, template, context)
