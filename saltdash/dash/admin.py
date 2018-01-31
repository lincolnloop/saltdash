from django.contrib import admin
from django.contrib.admin.decorators import register

from . import models


class SuccessFilter(admin.SimpleListFilter):
    title = 'success'
    parameter_name = 'success'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.successes()
        if self.value() == '0':
            return queryset.failures()


@register(models.Result)
class ResultAdmin(admin.ModelAdmin):
    list_filter = [SuccessFilter, 'fun', 'minion']
    list_display = ['jid', 'fun', 'minion', 'completed', 'success_method']

    def success_method(self, obj):
        return obj.was_success
    success_method.boolean = True
    success_method.short_description = 'success'


@register(models.Job)
class JobAdmin(admin.ModelAdmin):
    pass


