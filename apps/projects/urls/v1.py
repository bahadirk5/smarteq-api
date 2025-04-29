# apps/projects/urls/v1.py
from rest_framework.routers import DefaultRouter
from apps.projects.views.project_views import ProjectViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

urlpatterns = router.urls
