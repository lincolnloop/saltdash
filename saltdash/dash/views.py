from django.conf import settings
from django.core.paginator import InvalidPage, Page, Paginator
from django.db.models import QuerySet
from django.http import (
    Http404,
    HttpRequest,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Job, Result

ITEMS_PER_PAGE = 25


def paginate_queryset(queryset: QuerySet, request: HttpRequest) -> dict:
    """Paginate the queryset, if needed."""
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get("page") or 1
    try:
        page_number = int(page)
    except ValueError:
        if page == "last":
            page_number = paginator.num_pages
        else:
            raise Http404("Page is not 'last', nor can it be converted to an int.")
    try:
        page = paginator.page(page_number)
        return {
            "paginator": paginator,
            "page_obj": page,
            "object_list": page.object_list,
            "is_paginated": page.has_other_pages(),
        }
    except InvalidPage as e:
        raise Http404(
            "Invalid page ({page_number}): {exp}".format(
                page_number=page_number, exp=str(e)
            )
        )


def get_started(request):
    template = "dash/get_started.html"
    print(settings.DATABASES["default"])
    context = {
        "host": settings.DATABASES["default"]["HOST"] or "localhost",
        "name": settings.DATABASES["default"]["NAME"],
        "port": settings.DATABASES["default"]["PORT"] or 5432,
        "user": settings.DATABASES["default"]["USER"] or None,
    }
    return render(request, template, context)


def job_list(request):
    template = "dash/job_list.html"
    qs = Job.objects.all()
    show_system = "system" in request.GET
    if not show_system:
        qs = qs.exclude(load__fun="saltutil.find_job")
    context = {"job_list": qs, "has_system_jobs": show_system}
    context.update(paginate_queryset(qs, request))
    return render(request, template, context)


def job_detail(request, jid, success=None):
    template = "dash/job_detail.html"
    job = get_object_or_404(Job, jid=jid)
    filters = {"jid": jid}
    if success is not None:
        filters["success"] = success
    qs = Result.objects.filter(**filters)
    count = qs.count()
    if count == 1:
        return HttpResponseRedirect(
            reverse(
                "dash:result_detail", kwargs={"jid": qs[0].jid, "minion": qs[0].minion}
            )
        )
    context = {"job": job, "result_list": qs}
    context.update(paginate_queryset(qs, request))
    return render(request, template, context)


def result_list(request):
    template = "dash/result_list.html"
    qs = Result.objects.all()
    filters = {}
    show_system = "system" in request.GET
    if not show_system:
        qs = qs.exclude(fun="saltutil.find_job")
    if "minion" in request.GET:
        filters["minion"] = request.GET["minion"]
    qs = qs.filter(**filters)
    context = {"result_list": qs, "filters": filters, "has_system_jobs": show_system}
    context.update(paginate_queryset(qs, request))
    return render(request, template, context)


def result_detail(request, jid, minion):
    template = "dash/result_detail.html"
    result = get_object_or_404(Result, jid=jid, minion=minion)
    context = {"job": result.job, "result": result}
    return render(request, template, context)
