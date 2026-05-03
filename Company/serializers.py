# serializers.py
from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.username", read_only=True)

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = ["company", "created_at"]