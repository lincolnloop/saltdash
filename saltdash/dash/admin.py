from django.contrib import admin
from django.contrib.admin.decorators import register

from . import models


@register(models.Result)
class ResultAdmin(admin.ModelAdmin):
    list_filter = ['success', 'fun', 'minion']
    list_display = ['jid', 'fun', 'minion', 'completed', 'success']


@register(models.Job)
class JobAdmin(admin.ModelAdmin):
    pass


