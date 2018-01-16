from django.http import HttpResponseRedirect, Http404, \
    HttpResponsePermanentRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import JobID, SaltReturn


def job_list(request):
    template = "dash/job_list.html"
    qs = JobID.objects.all()
    show_system = 'system' in request.GET
    if not show_system:
        qs = qs.exclude(load__fun='saltutil.find_job')
    context = {
        'job_list': qs,
        'has_system_jobs': show_system,
    }
    return render(request, template, context)


def state_list(request):
    template = "dash/state_list.html"
    qs = SaltReturn.objects.filter(fun__startswith=['state.'])
    return render(request, template, {'state_list': qs})


def job_detail(request, jid, success=None):
    template = "dash/job_detail.html"
    job = get_object_or_404(JobID, jid=jid)
    filters = {'jid': jid}
    if success is not None:
        filters['success'] = success
    qs = SaltReturn.objects.filter(**filters)
    count = qs.count()
    if count == 1:
        return HttpResponseRedirect(
            reverse('dash:return_detail', kwargs={'pk': qs[0].pk}))
    if count == 0:
        raise Http404
    context = {
        'job': job,
        'return_list': qs,
    }
    return render(request, template, context)


def job_return_for_minion(request, jid,minion):
    template = "dash/job_detail.html"
    result = get_object_or_404(SaltReturn, jid=jid, id=minion)
    return HttpResponsePermanentRedirect(result.get_absolute_url())


def return_detail(request, pk):
    template = "dash/return_detail.html"
    ret = get_object_or_404(SaltReturn, pk=pk)
    context = {
        'job': ret.job,
        'return': ret,
    }
    return render(request, template, context)
