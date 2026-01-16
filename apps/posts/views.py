from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from .models import Post
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer,
)
from .permissions import IsAuthorOrAdmin
from .filters import PostFilter


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
        description=(
            "Retrieve a paginated list of blog posts. "
            "Published posts are public. "
            "Draft posts are visible only to authenticated users when explicitly requested."
        ),
        parameters=[
            OpenApiParameter("page", int, description="Page number"),
            OpenApiParameter("page_size", int, description="Number of items per page"),
            OpenApiParameter("search", str, description="Search in title and content"),
            OpenApiParameter("category", str, description="Filter by category slug"),
            OpenApiParameter("tag", str, description="Filter by tag slug"),
            OpenApiParameter("author", str, description="Filter by author username"),
            OpenApiParameter(
                "status",
                str,
                enum=["draft", "published"],
                description=(
                    "Filter by post status. "
                    "Drafts require authentication."
                ),
            ),
            OpenApiParameter(
                "ordering",
                str,
                description="Order by id, title, or created_at. Prefix with '-' for descending.",
            ),
        ],
        responses={
            200: PostListSerializer(many=True),
            403: OpenApiResponse(description="Authentication required to view drafts"),
        },
    )


    def get(self, request):

        queryset = Post.objects.order_by("id") # .filter(is_deleted=False)

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

        # Filter
        filterset = PostFilter(request.GET, queryset=queryset)
        queryset = filterset.qs

        # Ordering
        ordering = request.query_params.get("ordering")
        allowed_ordering = ["id", "title", "created_at"]

        if ordering:
            field = ordering.lstrip("-")
            if field in allowed_ordering:
                queryset = queryset.order_by(ordering)

        # Pagination
        paginator = PostPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = PostListSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Create a post",
        description=(
            "Create a new blog post. "
            "Authentication is required. "
            "The authenticated user becomes the author."
        ),
        request=PostCreateUpdateSerializer,
        responses={
            201: PostDetailSerializer,
            400: OpenApiResponse(description="Invalid data or creation failed"),
            401: OpenApiResponse(description="Authentication required"),
        },
    )

    def post(self, request):
        serializer = PostCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            post = serializer.save(
                author=request.user,
                created_by=request.user,
            )
        except Exception:
            return Response(
                {"detail": "Post creation failed"},
                status=status.HTTP_400_BAD_REQUEST,
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
        description=(
            "Retrieve a single blog post by ID or slug. "
            "Published posts are public. "
            "Draft posts are visible only to their author or admins."
        ),
        responses={
            200: PostDetailSerializer,
            403: OpenApiResponse(description="Not allowed to view draft post"),
            404: OpenApiResponse(description="Post not found"),
        },
    )


    def get(self, request, *args, **kwargs):
        post = self.get_object(**kwargs)

        # Protect draft 
        if post.status == Post.Status.DRAFT:
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication required to view draft posts"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if not (
                request.user == post.author or request.user.is_staff
            ):
                return Response(
                    {"detail": "You do not have permission to view this draft"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(PostDetailSerializer(post).data)


    # Swagger
    @extend_schema(
        summary="Update post",
        description=(
            "Partially update a blog post. "
            "Only the author or an admin may update a post."
        ),
        request=PostCreateUpdateSerializer,
        responses={
            200: PostDetailSerializer,
            400: OpenApiResponse(description="Invalid data or update failed"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Post not found"),
        },
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

        try:
            post = serializer.save(updated_by=request.user)
        except Exception:
            return Response(
                {"detail": "Update failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        return Response(PostDetailSerializer(post).data)


    @extend_schema(
        summary="Delete post (soft delete)",
        description=(
            "Soft delete a blog post. "
            "This operation is idempotent."
        ),
        responses={
            204: OpenApiResponse(description="Post deleted successfully"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Post not found"),
        },
    )


    def delete(self, request, *args, **kwargs):
        post = self.get_object(**kwargs)
        self.check_object_permissions(request, post)

        if post.is_deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        post.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
