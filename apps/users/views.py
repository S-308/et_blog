from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer, UserCreateSerializer

class UserListCreateAPIView(APIView):
    """
    GET  (Public)
    POST (Public)
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="List users",
        description="List all users.",
        responses=UserSerializer(many=True),
    )

    def get(self, request):
        users = User.objects.all().order_by("id")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


    @extend_schema(
        summary="Register user",
        description="Create New User.",
        request=UserCreateSerializer,
        responses=UserSerializer,
    )

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class UserDetailAPIView(APIView):
    """
    GET 
    PUT
    DELETE
    """

    permission_classes = [permissions.AllowAny]

    def get_object(self, pk):
        return get_object_or_404(User.objects, pk=pk)

    @extend_schema(
        summary="Retrieve user",
        description="Retrieve a user by ID.",
        responses=UserSerializer,
    )

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @extend_schema(
        summary="Update user",
        description="Update user details",
        request=UserSerializer,
        responses=UserSerializer,
    )

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)

    @extend_schema(
        summary="Delete user",
        description="Delete a user account",
    )

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
