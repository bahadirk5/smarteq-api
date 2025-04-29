# apps/projects/serializers/project_serializer.py
from rest_framework import serializers
from apps.projects.models.project import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
