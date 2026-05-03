# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', CompanyProfileView.as_view()),
    path('create_jobs/', CreateJobView.as_view(),name='create-job'),
    path('job_list/', CompanyJobListView.as_view(), name='job_list'),
    path('applicants/', CompanyApplicantsView.as_view(),name='applicants'),
    path('update-status/', UpdateApplicationStatusView.as_view(),name='update-status'),
]