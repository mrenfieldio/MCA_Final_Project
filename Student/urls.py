from django.urls import path
from . views import *

urlpatterns = [
    path('', StudentListAPIView.as_view(), name='student-home'),
    path('register/', RegisterStudentView.as_view(),name='student-register'),
]