from django.urls import path
from . views import *

urlpatterns = [
    path('profile/', StudentDetailAPIView.as_view(), name='student-home'),
    path('register/', RegisterStudentView.as_view(),name='student-register'),
    path('recommended-jobs/', RecommendedJobsView.as_view(), name='recommended-jobs'),
    path('apply-job/', ApplyJobView.as_view(), name='apply-job'),
    path("notifications/", StudentNotificationView.as_view(), name="student-notifications"),
    path("notifications/read/", MarkNotificationReadView.as_view(), name="mark-notification-read"),
    path("job-search/", JobSearchView.as_view(),name="job-search"),
    path("saved-jobs/", SavedJobsView.as_view(), name="saved-jobs"),
    path("save-job/", SaveJobView.as_view(), name="save-job"),

]