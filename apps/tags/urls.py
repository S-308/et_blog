from django.urls import path
from .views import (
    TagListAPIView,
    TagDetailAPIView,
    TagCreateAPIView,
    TagUpdateDeleteAPIView,
)

urlpatterns = [
    path("tags/", TagListAPIView.as_view()),
    path("tags/create/", TagCreateAPIView.as_view()),
    path("tags/<slug:slug>/", TagDetailAPIView.as_view()),
    path("tags/<slug:slug>/manage/", TagUpdateDeleteAPIView.as_view()),
]

