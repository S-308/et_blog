from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer, UserCreateSerializer
from rest_framework.pagination import PageNumberPagination
from .filters import UserFilter


class UserPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

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
        users = User.objects.order_by("id")     # .filter(is_deleted=False).

        filterset = UserFilter(request.GET, queryset=users)
        queryset = filterset.qs

        paginator = UserPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = UserSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Register user",
        description="Create New User.",
        request=UserCreateSerializer,
        responses=UserSerializer,
    )

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = serializer.save()
        except Exception as e:
            return Response(
                {"detail": "User creation failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        # GUARD: prevent update of deleted user
        if user.is_deleted:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save(updated_by=request.user)
        except Exception:
            return Response(
                {"detail": "Update failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(serializer.data)

    @extend_schema(
        summary="Delete user",
        description="Delete a user account",
    )

    def delete(self, request, pk):
        user = self.get_object(pk)

        # GUARD: idempotent delete
        if user.is_deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)