from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from apps.posts.models import Post
from .models import Comment
from .serializers import (
    CommentListSerializer,
    CommentCreateSerializer,
    CommentDetailSerializer,
)
from .permissions import IsAuthorOrAdmin
from .throttles import CommentRateThrottle
from rest_framework.pagination import PageNumberPagination

class CommentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

class PostCommentListAPIView(APIView):
    """
    GET  (Public)
    POST (Authenticated)
    """

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_throttles(self):
        if self.request.method == "POST":
            return [CommentRateThrottle()]
        return super().get_throttles()

    @extend_schema(
        summary="List comments for a post",
        description="Retrieve all comments associated with a specific post.",
        parameters=[
            OpenApiParameter(
                name="slug",
                description="Post slug",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
        responses=CommentListSerializer(many=True),
    )

    def get(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        comments = post.comments.all().order_by("id")
        paginator = CommentPagination()
        page = paginator.paginate_queryset(comments, request)
        serializer = CommentListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        summary="Create comment",
        description="Create a comment on a post. Rate limited.",
        parameters=[
            OpenApiParameter(
                name="slug",
                description="Post slug",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
        request=CommentCreateSerializer,
        responses=CommentDetailSerializer,
    )

    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save(
            post=post,
            author=request.user,
            created_by=request.user,
        )

        return Response(
            CommentDetailSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )

class CommentDetailAPIView(APIView):
    """
    PATCH  → (Author/Admin)
    DELETE → (Author/Admin)
    """

    permission_classes = [IsAuthenticated, IsAuthorOrAdmin]

    def get_object(self, id):
        try:
            return Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            return None
        
    @extend_schema(
        summary="Update comment",
        description="Update an existing comment (author or admin only).",
        parameters=[
            OpenApiParameter(
                name="id",
                description="Comment ID",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            )
        ],
        request=CommentCreateSerializer,
        responses=CommentDetailSerializer,
    )

    def patch(self, request, id):
        comment = self.get_object(id)
        if not comment:
            return Response(
                {"detail": "Comment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, comment)

        serializer = CommentCreateSerializer(
            comment,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        comment = serializer.save()
        comment.updated_by = request.user
        comment.save(update_fields=["updated_by"])

        return Response(
            CommentDetailSerializer(comment).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Delete comment",
        description="Delete a comment (author or admin only).",
        parameters=[
            OpenApiParameter(
                name="id",
                description="Comment ID",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            )
        ],
    )

    def delete(self, request, id):
        comment = self.get_object(id)
        if not comment:
            return Response(
                {"detail": "Comment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, comment)
        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
