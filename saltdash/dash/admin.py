from django.contrib import admin
from django.contrib.admin.decorators import register

from . import models


@register(models.SaltReturn)
class SaltReturnAdmin(admin.ModelAdmin):
    list_filter = ['success', 'fun', 'id']
    list_display = ['jid', 'fun', 'id', 'completed', 'success']


@register(models.JobID)
class JobIDAdmin(admin.ModelAdmin):
    pass


