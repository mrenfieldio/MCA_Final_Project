from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication 
from Company.models import Job
from .models import *
from django.db.models import Q


User = get_user_model()


class StudentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 

    def get(self, request):
        try:
            # Get the logged-in user
            user = request.user
            # print(f"{user.username} - Fetching student profile")
            
            # Check if user is a student
            if user.role != 'student':
                return Response(
                    {"error": "User is not a student"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get or create student profile
            student_profile, created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'name': user.get_full_name() or user.username,
                    'email': user.email,
                }
            )
            
            # if created:
            #     print(f"Created new profile for {user.username}")
            
            # Calculate profile completion percentage
            profile_complete = self.calculate_profile_completion(student_profile)
            
            # Prepare response data - safely handle all fields
            data = {
                "id": student_profile.id,
                # "username": user.username,  
                "email": user.username,
                "name": student_profile.name or "",
                "university": student_profile.university or "",
                "skills": student_profile.skills if student_profile.skills else [],
                "profile_picture": student_profile.profile_picture.url if student_profile.profile_picture and hasattr(student_profile.profile_picture, 'url') else None,
                "phone": student_profile.phone or "",
                "bio": student_profile.bio or "",
                "resume": request.build_absolute_uri(student_profile.resume.url) if student_profile.resume else None,
                "graduation_year": student_profile.graduation_year,
                "major": student_profile.major or "",
                "profile_complete_percentage": profile_complete
            }
            
            # print(f"Successfully fetched profile for {user.username}")
            return Response(data, status=status.HTTP_200_OK)
            
        except StudentProfile.DoesNotExist:
            return Response(
                {"error": "Student profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error in StudentDetailAPIView: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Server error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
    def put(self, request):
        try:
            user = request.user

            if user.role != 'student':
                return Response({"error": "User is not a student"}, status=403)

            student_profile = StudentProfile.objects.get(user=user)

            # TEXT DATA
            data = request.data

            if 'name' in data:
                student_profile.name = data['name']
            if 'university' in data:
                student_profile.university = data['university']
            if 'phone' in data:
                student_profile.phone = data['phone']
            if 'bio' in data:
                student_profile.bio = data['bio']
            if 'major' in data:
                student_profile.major = data['major']
            if 'graduation_year' in data:
                student_profile.graduation_year = data['graduation_year']

            # SKILLS (handle JSON string)
            if 'skills' in data:
                import json
                skills = data['skills']
                if isinstance(skills, str):
                    skills = json.loads(skills)
                student_profile.skills = skills

            # FILES 🔥
            if 'profile_picture' in request.FILES:
                student_profile.profile_picture = request.FILES['profile_picture']

            if 'resume' in request.FILES:
                student_profile.resume = request.FILES['resume']

            student_profile.save()

            return self.get(request)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
    
    def calculate_profile_completion(self, profile):
        """Calculate profile completion percentage"""
        total_fields = 0
        filled_fields = 0
        
        # Define fields to check
        fields_to_check = {
            'name': profile.name,
            'email': profile.email,
            'university': profile.university,
            'phone': profile.phone,
            'bio': profile.bio,
            'major': profile.major,
            'graduation_year': profile.graduation_year,
            'skills': profile.skills and len(profile.skills) > 0,
            'profile_picture': profile.profile_picture,
            'resume': profile.resume
        }
        
        for field_name, field_value in fields_to_check.items():
            total_fields += 1
            if field_value:
                filled_fields += 1
        
        if total_fields == 0:
            return 0
        
        return int((filled_fields / total_fields) * 100)



class RegisterStudentView(APIView):

    def post(self, request):
        data = request.data

        username = data.get("username")
        password = data.get("password")
        name = data.get("name")
        university = data.get("university")

        # 🔴 validation
        if not username or not password:
            return Response({"error": "Missing fields"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "User already exists"}, status=400)

        # ✅ create user
        user = User.objects.create_user(
            username=username,
            password=password,
            role="student"
        )

        # ✅ create profile
        StudentProfile.objects.create(
            user=user,
            name=name,
            university=university
        )

        return Response({"message": "Student Registered Successfully"}, status=201)
    


class RecommendedJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            student = StudentProfile.objects.get(user=user)

            student_skills = [skill.lower().strip() for skill in student.skills]
            student_degree = student.major.lower()

            jobs = Job.objects.all()

            matched_jobs = []

            for job in jobs:
                job_skills = [skill.lower().strip() for skill in job.skills.split(",")]
                job_degree = job.qualification.lower()

                # 🔥 Skill match (at least one skill matches)
                skill_match = any(
                    skill.strip() in job_skills for skill in student_skills
                )

                # 🔥 Degree match
                degree_match = student_degree in job_degree

                if skill_match or degree_match:
                    matched_jobs.append({
                        "id": job.id,
                        "title": job.title,
                        "location": job.location,
                        "job_type": job.job_type,
                        "description": job.description,
                        "skills": job.skills,
                        "experience": job.experience,
                        "qualification": job.qualification,
                        "work_mode": job.work_mode,
                        "deadline": job.deadline,
                        "skills": job.skills,
                        "salary": job.salary,
                        "company": job.company.companyprofile.company_name,
                        "created_at": job.created_at.isoformat(),
                    })

            return Response(matched_jobs)

        except StudentProfile.DoesNotExist:
            return Response({"error": "Student profile not found"}, status=404)
        
class ApplyJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        job_id = request.data.get("job")

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=404)

        # 🔥 Prevent duplicate apply
        if AppliedJobs.objects.filter(student=user, job=job).exists():
            return Response(
                {"error": "You already applied for this job"},
                status=status.HTTP_400_BAD_REQUEST
            )

       
        resume_file = request.FILES.get("resume")

        if not resume_file:
            try:
                student_profile = StudentProfile.objects.get(user=user)
                resume_file = student_profile.resume
            except StudentProfile.DoesNotExist:
                resume_file = None

        application = AppliedJobs.objects.create(
            student=user,
            job=job,
            full_name=request.data.get("full_name"),
            email=request.data.get("email"),
            phone=request.data.get("phone"),
            cover_letter=request.data.get("cover_letter"),
            resume=resume_file,   
            portfolio=request.data.get("portfolio"),
        )

        return Response({
            "message": "Application submitted successfully",
        }, status=201)
        
    def get(self, request):
        user = request.user

        jobs = AppliedJobs.objects.filter(student=user)

        data = []
        for obj in jobs:
            data.append({
                "id": obj.id,
                "job": {
                    "title": obj.job.title,
                    "company": obj.job.company.companyprofile.company_name,
                    'salary': obj.job.salary,
                    'deadline': obj.job.deadline,
                    'location': obj.job.location,
                    'description': obj.job.description,
                },
                # "status": obj.status,
                "applied_at": obj.applied_at.strftime("%Y-%m-%d"),
            })

        return Response(data)
    
class StudentNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by("-created_at")

        data = [
            {
                "id": n.id,
                "message": n.message,
                "read": n.is_read,
                "time": n.created_at.strftime("%b %d, %I:%M %p"),
            }
            for n in notifications
        ]

        return Response(data)
    
class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        notif_id = request.data.get("id")

        if not notif_id:
            return Response({"error": "Notification ID required"}, status=400)

        updated = Notification.objects.filter(
            id=notif_id,
            user=request.user
        ).update(is_read=True)

        if not updated:
            return Response({"error": "Notification not found"}, status=404)

        return Response({"message": "Marked as read"})
    



class JobSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search = request.GET.get("search", "")
        location = request.GET.get("location", "")

        jobs = Job.objects.all()

        #
        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(skills__icontains=search) |
                Q(company__companyprofile__company_name__icontains=search)
            )

        
        if location:
            jobs = jobs.filter(location__icontains=location)

        data = []
        for job in jobs:
            data.append({
                "id": job.id,
                "title": job.title,
                "company": job.company.companyprofile.company_name,
                "location": job.location,
                'description': job.description,
                'deadline': job.deadline,
                "salary": job.salary,
                "job_type": job.job_type,
                "created_at": job.created_at.isoformat(),
            })

        return Response(data)
    
class SaveJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        job_id = request.data.get("job_id")

        job = Job.objects.get(id=job_id)

        saved = SavedJob.objects.filter(user=user, job=job)

        if saved.exists():
            saved.delete()
            return Response({"saved": False})
        else:
            SavedJob.objects.create(user=user, job=job)
            return Response({"saved": True})
        
class SavedJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        jobs = SavedJob.objects.filter(user=request.user)

        data = [
            {
                "id": obj.id,
                "job": {
                    "id": obj.job.id,
                    "title": obj.job.title,
                    "company": obj.job.company.companyprofile.company_name,
                    "location": obj.job.location,
                    "description": obj.job.description,
                    "deadline": obj.job.deadline,
                    "salary": obj.job.salary,
                    "job_type": obj.job.job_type,
                    "created_at": obj.job.created_at.isoformat(),
                },
            }
            for obj in jobs
        ]

        return Response(data)