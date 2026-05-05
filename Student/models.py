from django.db import models
from django.conf import settings




User = settings.AUTH_USER_MODEL


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    university = models.CharField(max_length=255, blank=True, null=True)
    skills = models.JSONField(default=list, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    major = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


STATUS_CHOICES = [
    ('applied',     'Applied'),
    ('shortlisted', 'Shortlisted'),
    ('assessment',  'Assessment'),
    ('interview',   'Interview'),
    ('accepted',    'Accepted'),
    ('rejected',    'Rejected'),
]


class AppliedJobs(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    job     = models.ForeignKey(
        "Company.Job",             
        on_delete=models.CASCADE,
    )

    full_name    = models.CharField(max_length=255)
    email        = models.EmailField()
    phone        = models.CharField(max_length=20)

    cover_letter = models.TextField(blank=True, null=True)
    resume       = models.FileField(upload_to="applications/resumes/")
    portfolio    = models.URLField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied',
    )

    applied_at      = models.DateTimeField(auto_now_add=True)
    interview_date  = models.DateTimeField(null=True, blank=True)
    assessment_link = models.URLField(null=True, blank=True)
    message         = models.TextField(null=True, blank=True)


class Notification(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
    
class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey("Company.Job", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)