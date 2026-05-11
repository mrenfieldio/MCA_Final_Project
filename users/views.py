from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from Student.models import StudentProfile
from Company.models import CompanyProfile

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny] 
    authentication_classes = [] 
    def post(self, request):
        data = request.data
        print("Received registration data:", data)  
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")

        name = data.get("name")
        university = data.get("university")
        company_name = data.get("company_name")

        if not username or not password or not role:
            return Response({"error": "Required fields missing"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"error": "User already exists"}, status=400)

        user = User.objects.create_user(
            username=username,
            password=password,
            role=role
        )

        if role == "student":
            StudentProfile.objects.create(
                user=user,
                name=name,
                university=university
            )

        elif role == "company":
            CompanyProfile.objects.create(
                user=user,
                company_name=company_name
            )

        return Response({"message": "Registered successfully"})
    
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  
    
    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")
            
            # print(f"=== Login Attempt ===")
            # print(f"Username: {username}")
            # print(f"Password provided: {'Yes' if password else 'No'}")
            
            # Check if username and password are provided
            if not username or not password:
                return Response(
                    {"error": "Username and password are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Try to authenticate
            user = authenticate(username=username, password=password)
            
            # print(f"Authentication result: {user}")
            
            if user is None:
                # Check if user exists in database
                user_exists = User.objects.filter(username=username).exists()
                # print(f"User exists in DB: {user_exists}")
                
                if user_exists:
                    user_obj = User.objects.get(username=username)
                    # print(f"User is active: {user_obj.is_active}")
                    # print(f"User role: {user_obj.role}")
                
                return Response(
                    {"error": "Invalid credentials. Please register first or check your password."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check if user is active
            if not user.is_active:
                return Response(
                    {"error": "User account is disabled"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "is_admin": user.is_superuser,
                "role": user.role,
                "user_id": user.id,
                "username": user.username
            }
            
            print(f"Login successful for user: {username}")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Login failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
