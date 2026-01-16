from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import Tag
from .serializers import TagListSerializer
from rest_framework.permissions import IsAdminUser
from .serializers import TagCreateUpdateSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework.pagination import PageNumberPagination
from .filters import TagFilter


class TagPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class TagListAPIView(APIView):
    """
    GET (Public)
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="List tags",
        description=(
            "Retrieve a paginated list of tags. "
            "This endpoint is public and supports filtering."
        ),
        parameters=[
            OpenApiParameter("page", int, description="Page number"),
            OpenApiParameter("page_size", int, description="Number of items per page"),
        ],
        responses={
            200: TagListSerializer(many=True),
        },
    )

    def get(self, request):
        tags = Tag.objects.order_by("id") # .filter(is_deleted=False)

        filterset = TagFilter(request.GET, queryset=tags)
        queryset = filterset.qs

        paginator = TagPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = TagListSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)



class TagDetailAPIView(APIView):
    """
    GET (Public)
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Retrieve tag",
        description="Retrieve a single tag by its slug.",
        parameters=[
            OpenApiParameter(
                name="slug",
                description="Tag slug",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            200: TagListSerializer,
            404: OpenApiResponse(description="Tag not found"),
        },
    )

    def get(self, request, slug):
        try:
            tag = Tag.objects.get(slug=slug)
        except Tag.DoesNotExist:
            return Response(
                {"detail": "Tag not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TagListSerializer(tag)
        return Response(serializer.data)


class TagCreateAPIView(APIView):
    """
    POST (Admin)
    """

    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="Create tag",
        description=(
            "Create a new tag. "
            "This endpoint is restricted to admin users."
        ),
        request=TagCreateUpdateSerializer,
        responses={
            201: TagListSerializer,
            400: OpenApiResponse(description="Invalid data or creation failed"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin privileges required"),
        },
    )

    def post(self, request):
        serializer = TagCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tag = serializer.save(created_by=request.user)
        except Exception:
            return Response(
                {"detail": "Tag creation failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            TagListSerializer(tag).data,
            status=status.HTTP_201_CREATED
        )


class TagUpdateDeleteAPIView(APIView):
    """
    PATCH  (Admin)
    DELETE (Admin)
    """

    permission_classes = [IsAdminUser]

    def get_object(self, slug):
        try:
            return Tag.objects.get(slug=slug)
        except Tag.DoesNotExist:
            return None

    @extend_schema(
        summary="Update tag",
        description=(
            "Update an existing tag. "
            "This endpoint is restricted to admin users."
        ),
        parameters=[
            OpenApiParameter(
                name="slug",
                description="Tag slug",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
        request=TagCreateUpdateSerializer,
        responses={
            200: TagListSerializer,
            400: OpenApiResponse(description="Invalid data"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin privileges required"),
            404: OpenApiResponse(description="Tag not found"),
        },
    )

    def patch(self, request, slug):
        tag = self.get_object(slug)
        if not tag:
            return Response(
                {"detail": "Tag not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TagCreateUpdateSerializer(
            tag,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        tag = serializer.save()
        tag.updated_by = request.user
        tag.save(update_fields=["updated_by"])

        return Response(TagListSerializer(tag).data)
    
    @extend_schema(
        summary="Delete tag",
        description=(
            "Delete a tag. "
            "This operation is idempotent and restricted to admin users."
        ),
        parameters=[
            OpenApiParameter(
                name="slug",
                description="Tag slug",
                required=True,
                type=str,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            204: OpenApiResponse(description="Tag deleted successfully"),
            401: OpenApiResponse(description="Authentication required"),
            403: OpenApiResponse(description="Admin privileges required"),
            404: OpenApiResponse(description="Tag not found"),
        },
    )

    def delete(self, request, slug):
        tag = self.get_object(slug)
        if not tag:
            return Response(
                {"detail": "Tag not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        if tag.is_deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)

        tag.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
