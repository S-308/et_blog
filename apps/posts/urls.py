from django.urls import path
from .views import PostListCreateAPIView, PostDetailAPIView

urlpatterns = [
    path("posts/", PostListCreateAPIView.as_view()),
    path("posts/<int:id>/", PostDetailAPIView.as_view()),
    path("posts/<slug:slug>/", PostDetailAPIView.as_view()),
]
