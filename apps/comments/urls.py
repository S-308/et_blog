from django.urls import path
from .views import PostCommentListAPIView, CommentDetailAPIView

urlpatterns = [
    path("posts/<slug:slug>/comments/",PostCommentListAPIView.as_view(),name="post-comments",),
    path("comments/<int:id>/",CommentDetailAPIView.as_view(),name="comment-detail",),
]
