from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Post
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer,
)
from .permissions import IsAuthorOrAdmin


class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class PostListCreateAPIView(APIView):
    """
    GET  (Public)
    POST (Authenticated)
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsAuthorOrAdmin()]

    # Swagger
    @extend_schema(
        summary="List posts",
        description="List blog posts with search, filters, sorting and pagination.",
        parameters=[
            OpenApiParameter("page", int),
            OpenApiParameter("page_size", int),
            OpenApiParameter("search", str, description="Search title & content"),
            OpenApiParameter("category", str, description="Category slug"),
            OpenApiParameter("tag", str, description="Tag slug"),
            OpenApiParameter("author", str, description="Author username"),
            OpenApiParameter(
                "status",
                str,
                enum=["draft", "published"],
                description="Post status",
            ),
            OpenApiParameter(
                "ordering",
                str,
                description="Order by field (id, title, created_at). Use - for desc.",
            ),
        ],
        responses=PostListSerializer(many=True),
    )

    def get(self, request):

        queryset = Post.objects.filter(is_deleted=False).order_by("id")

        # Status 
        status_param = request.query_params.get("status")

        if status_param == Post.Status.DRAFT:
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication required to view drafts"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            queryset = queryset.filter(status=Post.Status.DRAFT)
        else:
            queryset = queryset.filter(status=Post.Status.PUBLISHED)

        # Search
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )

        # Filters
        category = request.query_params.get("category")
        tag = request.query_params.get("tag")
        author = request.query_params.get("author")

        if category:
            queryset = queryset.filter(category__slug=category)

        if tag:
            queryset = queryset.filter(tags__slug=tag)

        if author:
            queryset = queryset.filter(author__username=author)

        queryset = queryset.distinct()

        # Ordering
        ordering = request.query_params.get("ordering")
        allowed_ordering = ["id", "title", "created_at"]

        if ordering:
            field = ordering.lstrip("-")
            if field in allowed_ordering:
                queryset = queryset.order_by(ordering)

        # Pagination
        paginator = PageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = PostListSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)
    
    @extend_schema(
        summary="Create a post",
        request=PostCreateUpdateSerializer,
        responses=PostDetailSerializer,
    )

    def post(self, request):
        serializer = PostCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = serializer.save(
            author=request.user,
            created_by=request.user,
        )

        return Response(
            PostDetailSerializer(post).data,
            status=status.HTTP_201_CREATED,
        )


class PostDetailAPIView(APIView):
    """
    GET    (Public)
    PATCH  (Author/Admin)
    DELETE (Soft Delete)
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsAuthorOrAdmin()]

    def get_object(self, **kwargs):
        if "id" in kwargs:
            return get_object_or_404(Post, id=kwargs["id"], is_deleted=False)
        if "slug" in kwargs:
            return get_object_or_404(Post, slug=kwargs["slug"], is_deleted=False)

    # Swagger
    @extend_schema(
        summary="Retrieve post",
        responses=PostDetailSerializer,
    )

    def get(self, request, *args, **kwargs):
        post = self.get_object(**kwargs)
        return Response(PostDetailSerializer(post).data)

    # Swagger
    @extend_schema(
        summary="Update post",
        request=PostCreateUpdateSerializer,
        responses=PostDetailSerializer,
    )

    def patch(self, request, *args, **kwargs):
        post = self.get_object(**kwargs)
        self.check_object_permissions(request, post)

        serializer = PostCreateUpdateSerializer(
            post,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        post = serializer.save(updated_by=request.user)
        return Response(PostDetailSerializer(post).data)


    @extend_schema(
        summary="Delete post (soft delete)",
    )

    def delete(self, request, *args, **kwargs):
        post = self.get_object(**kwargs)
        self.check_object_permissions(request, post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
