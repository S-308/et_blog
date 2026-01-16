from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
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
from .filters import CommentFilter
from django.db.models import Prefetch


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
        description=(
            "Retrieve a paginated list of top-level comments for a post. "
            "Each comment may include nested replies. "
            "Comments on draft posts require authentication."
        ),
        parameters=[
            OpenApiParameter(
                name="slug",
                description="Post slug",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter("page", int, description="Page number"),
            OpenApiParameter("page_size", int, description="Number of items per page"),
        ],
        responses={
            200: CommentListSerializer(many=True),
            403: OpenApiResponse(
                description="Authentication required to view comments on draft posts"
            ),
            404: OpenApiResponse(description="Post not found"),
        },
    )


    def get(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if post.status == Post.Status.DRAFT:
            if not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication required to view comments on draft posts"},
                    status=status.HTTP_403_FORBIDDEN
                )

        comments = (
            Comment.objects
            .filter(post=post, parent__isnull=True)
            .select_related("author")
            .prefetch_related(      # Prefetch to save N+1 Queries - Save DB hit.
                Prefetch(
                    "replies",
                    queryset=Comment.objects
                    .select_related("author")       # ForeignKey
                    .order_by("id"),
                )
            )
            .order_by("id")
        )

        filterset = CommentFilter(request.GET, queryset=comments)
        queryset = filterset.qs

        paginator = CommentPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = CommentListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)


    @extend_schema(
        summary="Create comment",
        description=(
            "Create a comment on a published post. "
            "Supports nested replies using the parent field. "
            "This endpoint is rate limited."
        ),
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
        responses={
            201: CommentDetailSerializer,
            400: OpenApiResponse(description="Invalid data or creation failed"),
            403: OpenApiResponse(description="Comments are disabled for draft posts"),
            404: OpenApiResponse(description="Post not found"),
            429: OpenApiResponse(description="Rate limit exceeded"),
        },
    )

    def post(self, request, slug):
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response(
                {"detail": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Block commenting on drafts
        if post.status == Post.Status.DRAFT:
            return Response(
                {"detail": "Comments are disabled for draft posts"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CommentCreateSerializer(
            data=request.data,
            context={"post": post, "request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            comment = serializer.save(
                post=post,
                author=request.user,
                created_by=request.user,
            )
        except Exception:
            return Response(
                {"detail": "Comment creation failed"},
                status=status.HTTP_400_BAD_REQUEST,
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
        description=(
            "Update an existing comment. "
            "Only the comment author or an admin may update."
        ),
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
        responses={
            200: CommentDetailSerializer,
            400: OpenApiResponse(description="Invalid data"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Comment not found"),
        },
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
            partial=True,
            context={"post": comment.post, "request": request},
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
        description=(
            "Delete a comment. "
            "This operation is idempotent and allowed only for the author or admin."
        ),
        parameters=[
            OpenApiParameter(
                name="id",
                description="Comment ID",
                required=True,
                type=int,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            204: OpenApiResponse(description="Comment deleted successfully"),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Comment not found"),
        },
    )

    def delete(self, request, id):
        comment = self.get_object(id)
        if not comment:
            return Response(
                {"detail": "Comment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        self.check_object_permissions(request, comment)
        if comment.is_deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
                            
        comment.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
