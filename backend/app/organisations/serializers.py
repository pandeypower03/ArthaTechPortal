from rest_framework import serializers

from .models import Organisation, Project, Team, TeamMember

class MemberReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ["id", "name", "phone", "is_team_head", "is_active"]


class TeamReadSerializer(serializers.ModelSerializer):
    members = MemberReadSerializer(many=True)    # uses the prefetched members

    class Meta:
        model = Team
        fields = ["id", "name", "members"]

class ProjectSerializer(serializers.ModelSerializer):
    team_count = serializers.SerializerMethodField()
    remaining_paise = serializers.SerializerMethodField()

    teams = TeamReadSerializer(many=True)

    class Meta:
        model = Project
        # fields = ["id", "name", "project_type", "team_count", "record_count",
        #           "budget_paise", "actual_paise", "committed_paise", "remaining_paise"]
        fields = ["id", "name", "project_type", "team_count", "record_count",
                  "budget_paise", "actual_paise", "committed_paise", "remaining_paise", "teams"]

    def get_team_count(self, project):
        return len(project.teams.all())          # uses the prefetched teams, no extra query

    def get_remaining_paise(self, project):      # Budget - (Actual + Committed), as on your screen
        return project.budget_paise - (project.actual_paise + project.committed_paise)

class HouseSerializer(serializers.ModelSerializer):
    user_count = serializers.IntegerField()
    projects = ProjectSerializer(many=True)

    class Meta:
        model = Organisation
        fields = ["id", "name", "is_suspended", "suspended_reason",
                  "user_count", "projects"]