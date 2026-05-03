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

        # 🔥 Get only this company's jobs
        jobs = Job.objects.filter(company=user).order_by('-created_at')

        data = []
        for job in jobs:
            data.append({
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "job_type": job.job_type,
                "work_mode": job.work_mode,
                "salary": job.salary,
                "deadline": job.deadline,
                "created_at": job.created_at,
            })

        return Response(data)
    

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
        
        if new_status == "accepted":
            msg = f"Great news! You’ve moved forward for {application.job.title} by {application.job.company.companyprofile.company_name}."
        else:
            msg = f"Your application for {application.job.title} from {application.job.company.companyprofile.company_name} was reviewed, but not selected this time."

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

       
        if new_status == "accepted":
            template = "emails/ApplicationAccepted.html"
            subject = f" Selected - {application.job.title}"
        else:
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