from django.urls import path,include
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from . import views

urlpatterns = [
   path("",views.ManageSkill,name="manage_skill"),
]