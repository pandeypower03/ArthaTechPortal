from rest_framework import serializers

from .models import Organisation, Project


class ProjectSerializer(serializers.ModelSerializer):
    team_count = serializers.SerializerMethodField()
    remaining_paise = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "name", "project_type", "team_count", "record_count",
                  "budget_paise", "actual_paise", "committed_paise", "remaining_paise"]

    def get_team_count(self, project):
        return len(project.teams.all())          # uses the prefetched teams, no extra query

    def get_remaining_paise(self, project):      # Budget - (Actual + Committed), as on your screen
        return project.budget_paise - (project.actual_paise + project.committed_paise)


class HouseSerializer(serializers.ModelSerializer):
    plan = serializers.CharField(source="plan.name")
    plan_price_paise = serializers.IntegerField(source="plan.price_paise")
    user_count = serializers.IntegerField()
    projects = ProjectSerializer(many=True)

    class Meta:
        model = Organisation
        fields = ["id", "name", "plan", "plan_price_paise", "is_suspended",
                  "whatsapp_alerts", "bill_ocr", "tally_export", "multi_project_dashboard",
                  "user_count", "projects"]