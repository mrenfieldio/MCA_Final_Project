# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('profile/', CompanyProfileView.as_view()),
    path('create_jobs/', CreateJobView.as_view(),name='create-job'),
    path('job_list/', CompanyJobListView.as_view(), name='job_list'),
    path('applicants/', CompanyApplicantsView.as_view(),name='applicants'),
    path('update-status/', UpdateApplicationStatusView.as_view(),name='update-status'),
    path('dashboard/', CompanyDashboardView.as_view(), name='dashboard'),
    path("send-assessment/",SendAssessmentView.as_view(),name="send-assessment"),
    path("schedule-interview/",ScheduleInterviewView.as_view(),name="schedule-interview"),
    path("analytics/", CompanyAnalyticsView.as_view(),name="company-analytics"),
]