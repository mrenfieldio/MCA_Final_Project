from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Student.models import *
from django.contrib.auth import get_user_model
from Company.models import *
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class AdminStudentsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

       
        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        students = StudentProfile.objects.select_related(
            "user"
        )

        data = []

        for student in students:

            applications_count = AppliedJobs.objects.filter(
                student=student.user
            ).count()

            data.append({

                "id": student.id,

                "name": student.name,

                "email": student.user.username,

                "course": student.major,

                "skills": student.skills,

                "apps": applications_count,

                "status":
                    "active"
                    if student.user.is_active
                    else "inactive",

            })

        return Response(data)
    
class ToggleStudentStatusView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        
        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        try:

            student_profile = StudentProfile.objects.get(
                id=pk
            )

            user = student_profile.user

        except StudentProfile.DoesNotExist:

            return Response(
                {"error": "Student not found"},
                status=404
            )

        
        user.is_active = not user.is_active

        user.save()

        return Response({
            "message": "Student status updated",

            "status":
                "active"
                if user.is_active
                else "inactive"
        })
    
class DeleteStudentView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        
        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        try:

            student_profile = StudentProfile.objects.get(
                id=pk
            )

            user = student_profile.user

        except StudentProfile.DoesNotExist:

            return Response(
                {"error": "Student not found"},
                status=404
            )

        
        user.delete()

        return Response({
            "message": "Student deleted successfully"
        })

class AdminCompaniesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        companies = User.objects.filter(
            role="company"
        )

        data = []

        for company in companies:

            profile = CompanyProfile.objects.filter(
                user=company
            ).first()

            jobs_count = Job.objects.filter(
                company=company
            ).count()

            data.append({

                "id": company.id,

                "name":
                    profile.company_name
                    if profile else "N/A",

                # "industry":
                #     profile.industry
                #     if profile else "N/A",

                "email": company.username,

                "jobs": jobs_count,

                "status":
                    "approved"
                    if company.is_active
                    else "suspended",
            })

        return Response(data)



class UpdateCompanyStatusView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        status_value = request.data.get("status")

        try:

            company = User.objects.get(
                id=pk,
                role="company"
            )

        except User.DoesNotExist:

            return Response(
                {"error": "Company not found"},
                status=404
            )

        
        if status_value == "approved":

            company.is_active = True

        
        elif status_value == "suspended":

            company.is_active = False

        company.save()

        return Response({
            "message": "Company status updated"
        })



class DeleteCompanyView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        try:

            company = User.objects.get(
                id=pk,
                role="company"
            )

        except User.DoesNotExist:

            return Response(
                {"error": "Company not found"},
                status=404
            )

        company.delete()

        return Response({
            "message": "Company deleted"
        })
        


class AdminJobsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        
        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        jobs = Job.objects.all().order_by(
            "-created_at"
        )

        data = []

        for job in jobs:

            applications_count = AppliedJobs.objects.filter(
                job=job
            ).count()

            data.append({

                "id": job.id,

                "title": job.title,

                "company":
                    job.company.companyprofile.company_name,

                "type": job.job_type,

                "location": job.location,

                "posted":
                    job.created_at.strftime("%d %b %Y"),

                "apps": applications_count,

                "status":
                    "active"
                    if job.deadline >= timezone.now().date()
                    else "closed",
            })

        return Response(data)


class ToggleJobStatusView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        try:

            job = Job.objects.get(id=pk)

        except Job.DoesNotExist:

            return Response(
                {"error": "Job not found"},
                status=404
            )

        status_value = request.data.get("status")

        
        if status_value == "closed":

            job.deadline = timezone.now().date()

        
        elif status_value == "active":

            job.deadline = (
                timezone.now().date()
                + timedelta(days=30)
            )

        job.save()

        return Response({
            "message": "Job updated"
        })



class DeleteJobView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        if not request.user.is_superuser:
            return Response(
                {"error": "Unauthorized"},
                status=403
            )

        try:

            job = Job.objects.get(id=pk)

        except Job.DoesNotExist:

            return Response(
                {"error": "Job not found"},
                status=404
            )

        job.delete()

        return Response({
            "message": "Job deleted"
        })