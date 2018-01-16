from django.urls import path

from . import views

app_name = 'dash'

urlpatterns = [
    path('', views.job_list, name="job_list"),
    path('jid/<int:jid>/', views.job_detail, name="job_detail"),
    path('jid/<int:jid>/success/',
         views.job_detail,
         {'success': True},
         name="job_detail_success"),
    path('jid/<int:jid>/failure/',
         views.job_detail,
         {'success': False},
         name="job_detail_failed"),
    path('jid/<int:jid>/<str:minion>/',
         views.job_return_for_minion,
         name="job_return_for_minion"),
    path('return/<int:pk>/', views.return_detail, name="return_detail"),
]
