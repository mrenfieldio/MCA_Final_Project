# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Company.models import CompanyProfile
from Student.models import AppliedJobs,Notification
from .serializers import JobSerializer
from rest_framework import status
from .models import *
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.dateparse import parse_datetime
from django.utils import timezone



class CompanyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        try:
            company = CompanyProfile.objects.get(user=user)

            data = {
                "company_name": company.company_name,
                "email": user.email,
                # "location": company.location,
                # "description": company.description,
                # "logo": company.logo.url if company.logo else None
            }

            return Response(data)

        except CompanyProfile.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)
        
        


class CreateJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(company=request.user)
            return Response({
                "message": "Job created successfully",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class CompanyJobListView(APIView):
    permission_classes = [IsAuthenticated]

    
    def get(self, request):
        user = request.user
        jobs = Job.objects.filter(company=user).order_by('-created_at')

        data = []
        for job in jobs:
            data.append({
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "qualification": job.qualification,
                "experience": job.experience,
                "skills": job.skills,
                "description": job.description,
                "job_type": job.job_type,
                "work_mode": job.work_mode,
                "salary": job.salary,
                "deadline": job.deadline,
                "created_at": job.created_at,
            })

        return Response(data)

    
    def put(self, request):
        user = request.user
        job_id = request.data.get("job_id")

        try:
            job = Job.objects.get(id=job_id, company=user)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        
        job.title = request.data.get("title", job.title)
        job.description = request.data.get("description", job.description)

        job.location = request.data.get("location", job.location)
        job.job_type = request.data.get("job_type", job.job_type)
        job.work_mode = request.data.get("work_mode", job.work_mode)

        job.qualification = request.data.get("qualification", job.qualification)
        job.skills = request.data.get("skills", job.skills)
        job.experience = request.data.get("experience", job.experience)

        job.salary = request.data.get("salary", job.salary)
        job.deadline = request.data.get("deadline", job.deadline)

        job.save()

        return Response({"message": "Job updated successfully"})

    
    def delete(self, request):
        user = request.user
        job_id = request.data.get("job_id")

        try:
            job = Job.objects.get(id=job_id, company=user)  
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        job.delete()

        return Response({
            "message": "Job deleted successfully"
        }, status=200)
    

class CompanyApplicantsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        applications = AppliedJobs.objects.filter(
            job__company=user
        ).select_related("job", "student")

        data = []

        for app in applications:
            data.append({
                "id": app.id,
                "student_name": app.full_name,
                "email": app.email,
                "job_title": app.job.title,
                "status": app.status,
                "resume": request.build_absolute_uri(app.resume.url) if app.resume else None,
                
            })
            
        return Response(data)


class UpdateApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        app_id = request.data.get("application_id")
        new_status = request.data.get("status")

        try:
            application = AppliedJobs.objects.get(
                id=app_id,
                job__company=user
            )
        except AppliedJobs.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        application.status = new_status
        application.save()
        
        if new_status == "shortlisted":
            msg = f"🎉 You’ve been shortlisted for {application.job.title}"

        elif new_status == "assessment":
            msg = f"🧠 Complete the assessment for {application.job.title}"

        elif new_status == "interview":
            msg = f"📅 Interview scheduled for {application.job.title}"

        elif new_status == "accepted":
            msg = f"🚀 Congratulations! You are selected for {application.job.title}"

        elif new_status == "rejected":
            msg = f"❌ Application not selected for {application.job.title}"

        else:
           msg = f"Status updated for {application.job.title}"
        Notification.objects.create(
            user=application.student,
            message=msg
        )

        
        company_name = getattr(
            application.job.company.companyprofile,
            "company_name",
            application.job.company.username
        )

        context = {
            "name": application.full_name,
            "job_title": application.job.title,
            "company_name": company_name,
        }

       
        if new_status == "shortlisted":
            template = "emails/Shortlisted.html"
            subject = f"Shortlisted - {application.job.title}"

        elif new_status == "assessment":
            template = "emails/Assessment.html"
            subject = f"Assessment Round - {application.job.title}"

        elif new_status == "interview":
            template = "emails/Interview.html"
            subject = f"Interview Scheduled - {application.job.title}"

        elif new_status == "accepted":
            template = "emails/ApplicationAccepted.html"
            subject = f"Selected - {application.job.title}"

        elif new_status == "rejected":
            template = "emails/ApplicationRejected.html"
            subject = f"Application Update - {application.job.title}"

        
        html_content = render_to_string(template, context)

        email = EmailMultiAlternatives(
            subject,
            "",  
            "your_email@gmail.com",
            [application.email],
        )

        email.attach_alternative(html_content, "text/html")
        email.send()

        return Response({"message": "Status updated & email sent"})
    
class CompanyDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        jobs = Job.objects.filter(company=user)

        active_jobs = jobs.count()

        applications = AppliedJobs.objects.filter(job__company=user)

        total_applicants = applications.count()
        shortlisted = applications.filter(status="accepted").count()
        interviews = applications.filter(status="interview").count()  # optional

        
        job_data = []
        for job in jobs:
            job_data.append({
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "status": "active",
                "applicants": AppliedJobs.objects.filter(job=job).count(),
                "posted": job.created_at.strftime("%b %d"),
            })

        
        recent = applications.order_by("-applied_at")[:5]

        recent_data = []
        for app in recent:
            recent_data.append({
                "name": app.full_name,
                "role": app.job.title,
                "experience": app.job.experience,
                "status": app.status,
                "score": 85, 
            })

        return Response({
            "stats": {
                "active_jobs": active_jobs,
                "total_applicants": total_applicants,
                "interviews": interviews,
                "shortlisted": shortlisted,
            },
            "jobs": job_data,
            "recent_candidates": recent_data,
        })
        
class SendAssessmentView(APIView):
    permission_classes = [IsAuthenticated]
 
    def post(self, request):
        user = request.user
 
        app_id       = request.data.get("application_id")
        title        = request.data.get("title", "").strip()
        assess_type  = request.data.get("type", "mcq")
        instructions = request.data.get("instructions", "").strip()
        deadline_raw = request.data.get("deadline", "")
        link         = request.data.get("link", "").strip()
 
        # ── Validate required fields ──────────────────────────────────────────
        if not title:
            return Response({"error": "Assessment title is required."}, status=400)
        if not deadline_raw:
            return Response({"error": "Deadline is required."}, status=400)
 
        deadline = parse_datetime(deadline_raw)
        if not deadline:
            return Response({"error": "Invalid deadline format. Use ISO 8601."}, status=400)
        if timezone.is_naive(deadline):
            deadline = timezone.make_aware(deadline)
 
        # ── Fetch application (scoped to this company) ────────────────────────
        try:
            application = AppliedJobs.objects.select_related(
                "job", "job__company", "job__company__companyprofile"
            ).get(id=app_id, job__company=user)
        except AppliedJobs.DoesNotExist:
            return Response({"error": "Application not found."}, status=404)
 
        # ── Only allow sending assessment when candidate is shortlisted ────────
        if application.status != "shortlisted":
            return Response(
                {"error": f"Cannot send assessment. Current status is '{application.status}'. Candidate must be shortlisted first."},
                status=400,
            )
 
        # ── Save Assessment record ────────────────────────────────────────────
        # This lets you later build a submission/grading system on top of it.
        assessment = Assessment.objects.create(
            application=application,
            title=title,
            assess_type=assess_type,
            instructions=instructions,
            deadline=deadline,
            link=link,
        )
 
        # ── Advance application status → "assessment" ─────────────────────────
        application.status = "assessment"
        application.save()
 
        # ── In-app notification ───────────────────────────────────────────────
        Notification.objects.create(
            user=application.student,
            message=f"🧠 Complete the assessment for {application.job.title}: {title}",
        )
 
        # ── Email ─────────────────────────────────────────────────────────────
        company_name = getattr(
            application.job.company.companyprofile,
            "company_name",
            application.job.company.username,
        )
 
        TYPE_LABELS = {
            "mcq":    "Multiple Choice Quiz",
            "coding": "Coding Challenge",
            "file":   "Assignment / File Upload",
        }
 
        context = {
            "name":         application.full_name,
            "job_title":    application.job.title,
            "company_name": company_name,
            # Assessment-specific context
            "assessment_title":   title,
            "assessment_type":    TYPE_LABELS.get(assess_type, assess_type),
            "instructions":       instructions,
            "deadline":           deadline.strftime("%d %B %Y, %I:%M %p"),
            "assessment_link":    link or None,   # None → template hides the button
        }
 
        html_content = render_to_string("emails/Assessment.html", context)
 
        email = EmailMultiAlternatives(
            subject=f"Assessment Round — {application.job.title}",
            body="",
            from_email="your_email@gmail.com",
            to=[application.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
 
        return Response({
            "message": "Assessment sent successfully.",
            "assessment_id": assessment.id,
            "new_status": "assessment",
        })
 
 

class ScheduleInterviewView(APIView):
    permission_classes = [IsAuthenticated]
 
    def post(self, request):
        user = request.user
 
        app_id          = request.data.get("application_id")
        date_raw        = request.data.get("date", "")
        mode            = request.data.get("mode", "video")
        meeting_link    = request.data.get("meetingLink", "").strip()
        interviewer     = request.data.get("interviewerName", "").strip()
        notes           = request.data.get("notes", "").strip()
 
        # ── Validate ──────────────────────────────────────────────────────────
        if not date_raw:
            return Response({"error": "Interview date and time are required."}, status=400)
 
        interview_dt = parse_datetime(date_raw)
        if not interview_dt:
            return Response({"error": "Invalid date format. Use ISO 8601."}, status=400)
        if timezone.is_naive(interview_dt):
            interview_dt = timezone.make_aware(interview_dt)
 
        if mode == "video" and not meeting_link:
            return Response({"error": "Meeting link is required for video interviews."}, status=400)
 
        # ── Fetch application ─────────────────────────────────────────────────
        try:
            application = AppliedJobs.objects.select_related(
                "job", "job__company", "job__company__companyprofile"
            ).get(id=app_id, job__company=user)
        except AppliedJobs.DoesNotExist:
            return Response({"error": "Application not found."}, status=404)
 
        # ── Only allow scheduling after assessment stage ───────────────────────
        if application.status != "assessment":
            return Response(
                {"error": f"Cannot schedule interview. Current status is '{application.status}'. Assessment must be completed first."},
                status=400,
            )
 
        # ── Save Interview record ─────────────────────────────────────────────
        interview = Interview.objects.create(
            application=application,
            scheduled_at=interview_dt,
            mode=mode,
            meeting_link=meeting_link,
            interviewer_name=interviewer,
            notes=notes,
        )
 
        # ── Advance status → "interview" ──────────────────────────────────────
        application.status = "interview"
        application.save()
 
        # ── In-app notification ───────────────────────────────────────────────
        formatted_dt = interview_dt.strftime("%d %B %Y at %I:%M %p")
        Notification.objects.create(
            user=application.student,
            message=f"📅 Interview scheduled for {application.job.title} on {formatted_dt}",
        )
 
        # ── Email ─────────────────────────────────────────────────────────────
        company_name = getattr(
            application.job.company.companyprofile,
            "company_name",
            application.job.company.username,
        )
 
        MODE_LABELS = {
            "video":     "Video Call",
            "phone":     "Phone Call",
            "in-person": "In-Person",
        }
 
        context = {
            "name":         application.full_name,
            "job_title":    application.job.title,
            "company_name": company_name,
            "interview_date":     interview_dt.strftime("%A, %d %B %Y"),
            "interview_time":     interview_dt.strftime("%I:%M %p"),
            "interview_mode":     MODE_LABELS.get(mode, mode),
            "meeting_link":       meeting_link or None,
            "interviewer_name":   interviewer or None,
            "notes":              notes or None,
        }
 
        html_content = render_to_string("emails/Interview.html", context)
 
        email = EmailMultiAlternatives(
            subject=f"Interview Scheduled — {application.job.title}",
            body="",
            from_email="your_email@gmail.com",
            to=[application.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
 
        return Response({
            "message": "Interview scheduled successfully.",
            "interview_id": interview.id,
            "new_status": "interview",
        })