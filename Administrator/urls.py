from django.urls import path,include
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from . views import *

urlpatterns = [
      path("students/", AdminStudentsView.as_view(), name="admin-students"),
      path("students/<int:pk>/toggle-status/",ToggleStudentStatusView.as_view(), name="toggle-student-status"),
      path("students/<int:pk>/",DeleteStudentView.as_view(), name="delete-student"),
      path("companies/", AdminCompaniesView.as_view(), name="admin-companies"),
      path("companies/update-status/", UpdateCompanyStatusView.as_view(), name="update-company-status"),
      path("companies/delete/", DeleteCompanyView.as_view(), name="delete-company"),
      path("jobs/", AdminJobsView.as_view(), name="admin-jobs"),
      path("jobs/<int:pk>/status/", ToggleJobStatusView.as_view(), name="toggle-job-status"),
      path("jobs/<int:pk>/", DeleteJobView.as_view(), name="delete-job"),
]