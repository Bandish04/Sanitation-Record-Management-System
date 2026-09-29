from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsInspector, IsAdmin
from .serializers import SignupSerializer, LoginSerializer, UserSerializer, AdminUserSerializer
from audit.models import AuditLog
from django.contrib.auth.models import User, Group
from rest_framework import generics, status

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def admin_users_page(request):
    return render(request, "admin/users.html")

@login_required
def plants_page(request):
    return render(request, "plants/list.html")

@login_required
def sanitizer_page(request):
    return render(
        request,
        "titrations/sanitizer.html",
    )

@login_required
def daily_records_page(request):
    return render(request, "records/daily.html")

@login_required
def chloragel_page(request):
    return render(
        request,
        "titrations/chloragel.html",
    )
@login_required
def inspection_page(request):
    return render(
        request,
        "inspections/inspection.html",
    )
@login_required
def atp_page(request):
    return render(
        request,
        "inspections/atp.html",
    )
@login_required
def records_search_page(request):
    return render(
        request,
        "records/search.html",
    )

def browser_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:

            if not user.is_active:
                return render(
                    request,
                    "registration/login.html",
                    {
                        "error": "This account is inactive."
                    },
                )

            login(request, user)

            return redirect("dashboard")

        return render(
            request,
            "registration/login.html",
            {
                "error": "Invalid username or password."
            },
        )

    return render(
        request,
        "registration/login.html",
    )

def signup(request):

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("login")

    else:

        form = UserCreationForm()

    return render(
        request,
        "registration/signup.html",
        {"form": form}
    )


@login_required
def dashboard(request):

    return render(
        request,
        "dashboard.html"
    )

class SignupAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {
                    "message": "User created successfully.",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    }
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            AuditLog.objects.create(
             user=user,
             action="LOGIN",
             object_type="User",
             object_id=user.id,
             old_values=None,
             new_values={
             "username": user.username,
              },
            reason="User logged in successfully.",
            )

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Login successful.",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        serializer = UserSerializer(user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class InspectorTestAPIView(APIView):
    permission_classes = [IsInspector]

    def get(self, request):
        return Response(
            {
                "message": "Inspector access granted.",
                "user": request.user.username,
            },
            status=status.HTTP_200_OK,
        )

class AdminUserListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.prefetch_related("groups").order_by("id")

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        role = data.pop("role", None)

        if isinstance(role, list):
            role = role[0] if role else None

        if not role:
            return Response(
                {
                    "role": "Role is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed_roles = [
            "Inspector",
            "Team Lead",
            "Admin",
        ]

        if role not in allowed_roles:
            return Response(
                {
                    "role": (
                        "Invalid role. Choose Inspector, "
                        "Team Lead, or Admin."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        group = Group.objects.get(name=role)
        user.groups.add(group)

        AuditLog.objects.create(
            user=request.user,
            action="CREATE_USER",
            object_type="User",
            object_id=user.id,
            old_values=None,
            new_values={
                "username": user.username,
                "email": user.email,
                "role": role,
                "is_active": user.is_active,
            },
            reason="Admin created a new user.",
        )

        return Response(
            self.get_serializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class AdminUserDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.prefetch_related("groups").all()

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        old_role = user.groups.first().name if user.groups.first() else None

        old_values = {
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "role": old_role,
        }

        data = request.data.copy()

        role = data.pop("role", None)

        if isinstance(role, list):
            role = role[0] if role else None

        serializer = self.get_serializer(
            user,
            data=data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        user.refresh_from_db()

        if role is not None:
            allowed_roles = [
                "Inspector",
                "Team Lead",
                "Admin",
            ]

            if role not in allowed_roles:
                return Response(
                    {
                        "role": (
                            "Invalid role. Choose Inspector, "
                            "Team Lead, or Admin."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            group = Group.objects.get(name=role)

            user.groups.clear()
            user.groups.add(group)

        user.refresh_from_db()

        new_role = (
            user.groups.first().name
            if user.groups.first()
            else None
        )

        new_values = {
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "role": new_role,
        }

        AuditLog.objects.create(
            user=request.user,
            action="UPDATE_USER",
            object_type="User",
            object_id=user.id,
            old_values=old_values,
            new_values=new_values,
            reason="Admin updated user account.",
        )

        return Response(
            self.get_serializer(user).data,
            status=status.HTTP_200_OK,
        )