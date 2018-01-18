from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from . import views

app_name = 'dash'

urlpatterns = [
    # placeholder for dashboard
    path('', RedirectView.as_view(url=reverse_lazy('dash:job_list'))),
    path('get-started/', views.get_started, name="get_started"),
    path('job/', views.job_list, name="job_list"),
    path('job/<int:jid>/', views.job_detail, name="job_detail"),
    path('job/<int:jid>/success/',
         views.job_detail,
         {'success': True},
         name="job_detail_success"),
    path('job/<int:jid>/failure/',
         views.job_detail,
         {'success': False},
         name="job_detail_failed"),
    path('job/<int:jid>/<str:minion>/',
         views.result_detail,
         name="result_detail"),
    path('result/', views.result_list, name="result_list"),
]
