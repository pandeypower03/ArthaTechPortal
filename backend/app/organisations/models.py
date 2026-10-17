from django.conf import settings
from django.db import models
from django.db.models import Q

class Organisation(models.Model):                    # a production house
    name = models.CharField(max_length=150, unique=True)
    is_suspended = models.BooleanField(default=False)
    suspended_reason = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Project(models.Model):
    class Type(models.TextChoices):
        MOVIE = "movie"
        OTT_SERIES = "ott_series"
        AD = "ad"
        OTHER = "other"

    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT, related_name="projects")
    name = models.CharField(max_length=150)
    project_type = models.CharField(max_length=20, choices=Type.choices)
    # The next four are filled by the budget and expense modules later, never typed in
    budget_paise = models.BigIntegerField(default=0)
    actual_paise = models.BigIntegerField(default=0)
    committed_paise = models.BigIntegerField(default=0)
    record_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("organisation", "name")]

    def __str__(self):
        return self.name


class Team(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="teams")
    name = models.CharField(max_length=100)
    budget_paise = models.BigIntegerField(default=0)
    advance_paise = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("project", "name")]

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="members")
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    is_team_head = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             on_delete=models.PROTECT, related_name="team_memberships")  # empty = no login
    is_active = models.BooleanField(default=True)    # switch off, never delete
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # only one active team head per team
            models.UniqueConstraint(fields=["team"], condition=Q(is_team_head=True, is_active=True),
                                    name="one_active_head_per_team"),
        ]

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    """The diary. Lines are only added, never edited or deleted."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT)
    action = models.CharField(max_length=50)                    # "house.created", "login.failed"
    target_type = models.CharField(max_length=30, blank=True)   # "organisation", "team"...
    target_id = models.BigIntegerField(null=True, blank=True)
    details = models.JSONField(default=dict)                    # before and after, or the email tried
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]