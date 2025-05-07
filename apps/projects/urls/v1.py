from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.projects.views.project_views import ProjectViewSet
from apps.projects.views.project_inventory_views import ProjectInventoryViewSet

# DRF router for viewsets 
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'project-inventory', ProjectInventoryViewSet, basename='project-inventory')

# URL patterns 
urlpatterns = [
    path('', include(router.urls)),
]
