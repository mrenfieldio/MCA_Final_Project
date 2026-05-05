from django.db import models
from django.conf import settings

# ✅ Removed: from Student.models import AppliedJobs
# It was not used anywhere in this file.
# Assessment and Interview already use "Student.AppliedJobs" string — that's correct.

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

    skills = models.TextField()
    experience = models.CharField(max_length=100)

    salary = models.CharField(max_length=100)

    deadline = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)


class Assessment(models.Model):
    TYPE_CHOICES = [
        ("mcq",    "MCQ"),
        ("coding", "Coding Challenge"),
        ("file",   "File Upload"),
    ]

    application = models.OneToOneField(
        "Student.AppliedJobs",      # ✅ string reference — no import needed
        on_delete=models.CASCADE,
        related_name="assessment",
    )
    title        = models.CharField(max_length=255)
    assess_type  = models.CharField(max_length=20, choices=TYPE_CHOICES, default="mcq")
    instructions = models.TextField(blank=True)
    deadline     = models.DateTimeField()
    link         = models.URLField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assessment: {self.title} → {self.application}"


class Interview(models.Model):
    MODE_CHOICES = [
        ("video",     "Video Call"),
        ("phone",     "Phone Call"),
        ("in-person", "In-Person"),
    ]

    application = models.OneToOneField(
        "Student.AppliedJobs",      # ✅ string reference — no import needed
        on_delete=models.CASCADE,
        related_name="interview",
    )
    scheduled_at     = models.DateTimeField()
    mode             = models.CharField(max_length=20, choices=MODE_CHOICES, default="video")
    meeting_link     = models.CharField(max_length=500, blank=True)
    interviewer_name = models.CharField(max_length=150, blank=True)
    notes            = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview: {self.application} on {self.scheduled_at}"