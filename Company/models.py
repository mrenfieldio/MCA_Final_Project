from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.company_name
    
class Job(models.Model):
    company = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField()

    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50)  
    
    work_mode = models.CharField(max_length=50, default="onsite")
    
    qualification = models.CharField(max_length=100, default="Any")

    skills = models.TextField()  # comma separated or JSON
    experience = models.CharField(max_length=100)

    salary = models.CharField(max_length=100)

    deadline = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)