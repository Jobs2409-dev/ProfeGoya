# core/urls.py
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"projects", views.ProjectViewSet, basename="project")
router.register(r"tasks", views.TasksViewSet, basename="task")
 
urlpatterns = [
    path("", include(router.urls)),
]
