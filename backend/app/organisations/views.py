from django.db import IntegrityError, transaction
from django.db.models import Count, ProtectedError, Q
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.audit import log
from core.exceptions import AppError
from core.messages import get_message
from core.permissions import IsSuperUser , IsAdminOrAbove
from .excel_import import import_excel
from .models import AuditLog, Organisation, Project, Team, TeamMember
from .serializers import HouseSerializer


class HouseListView(APIView):
    """GET: all production houses with their projects (the 'Production houses' page)."""
    permission_classes = [IsAdminOrAbove]

    def get(self, request):
        houses = (Organisation.objects
                  .prefetch_related("projects__teams__members")
                  .annotate(user_count=Count("users", distinct=True))
                  .order_by("name"))
        return Response(HouseSerializer(houses, many=True).data)


class UploadView(APIView):
    """POST: form field 'file' = the .xlsx. Saves everything, or nothing if any row is wrong."""
    permission_classes = [IsAdminOrAbove]
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get("file")
        if not file or not file.name.lower().endswith(".xlsx"):
            raise AppError("FILE_BAD", 400)
        try:
            counts = import_excel(file)
        except ValueError as error:
            return Response({"code": "UPLOAD_HAS_ERRORS", "message": get_message("UPLOAD_HAS_ERRORS"),
                             "details": str(error)}, status=422)
        log(request, "house.excel_uploaded", details={"file": file.name, "created": counts})
        return Response({"code": "UPLOAD_SAVED", "message": get_message("UPLOAD_SAVED"), "created": counts}, status=201)


class CreateHouseView(APIView):
    """POST: one JSON with the house, its projects, teams and people. Saves all or nothing."""
    permission_classes = [IsAdminOrAbove]

    def post(self, request):
        data = request.data   # the JSON from the frontend, as a Python dictionary
        try:
            # "atomic" = if any line below fails, everything saved so far is undone
            with transaction.atomic():

                # 1. Production house
                org = Organisation.objects.create(name=data["name"])

                # 2. Projects of this house
                for p in data.get("projects", []):
                    if p["project_type"] not in Project.Type.values:
                        raise ValueError("project_type must be movie, ott_series, ad or other")
                    project = Project.objects.create(
                        organisation=org,
                        name=p["name"],
                        project_type=p["project_type"],
                    )

                    # 3. Teams of this project
                    for t in p.get("teams", []):
                        team = Team.objects.create(
                            project=project,
                            name=t["name"],
                            budget_paise=t.get("budget_paise", 0),
                            advance_paise=t.get("advance_paise", 0),
                        )

                        # 4. People of this team
                        for m in t.get("members", []):
                            TeamMember.objects.create(
                                team=team,
                                name=m["name"],
                                phone=m.get("phone", ""),
                                job_title=m.get("job_title", ""),
                                is_team_head=bool(m.get("is_team_head")),
                            )

                # 5. Audit log line, inside the same transaction
                log(request, "house.created", "organisation", org.id, {"name": org.name})

        except KeyError as error:
            return self.bad(f"Missing field: {error.args[0]}")
        except IntegrityError:
            return self.bad("A name is repeated (house, project or team), or a team has two heads.")
        except (ValueError, TypeError, AttributeError) as error:
            return self.bad(str(error) or "The data is not in the right format.")

        return Response({"code": "HOUSE_CREATED", "message": get_message("HOUSE_CREATED"), "id": org.id}, status=201)

    def bad(self, details):
        return Response({"code": "HOUSE_INVALID", "message": get_message("HOUSE_INVALID"),
                         "details": details}, status=422)


class RemoveView(APIView):
    """DELETE /api/organisations/remove/<type>/<id>/  where type = organisation, project, team or member"""
    permission_classes = [IsAdminOrAbove]

    def delete(self, request, kind, item_id):
        tables = {"organisation": Organisation, "project": Project,
                  "team": Team, "member": TeamMember}
        if kind not in tables:
            return self.blocked("type must be organisation, project, team or member")

        item = tables[kind].objects.filter(id=item_id).first()
        if item is None:
            raise AppError("NOT_FOUND", 404)
        name = str(item)   # keep the name now, the row may be gone in a moment

        if kind == "project" and (item.actual_paise or item.committed_paise):
            return self.blocked("This project has spending, so it cannot be removed.")

        try:
            with transaction.atomic():
                item.delete()
                log(request, f"{kind}.removed", kind, item_id, {"name": name})
        except ProtectedError:
            return self.blocked("It has something inside it (or is in use). Remove that first.")
        return self.removed()

    def removed(self):
        return Response({"code": "ITEM_REMOVED", "message": get_message("ITEM_REMOVED")})

    def blocked(self, details):
        return Response({"code": "REMOVE_BLOCKED", "message": get_message("REMOVE_BLOCKED"),
                         "details": details}, status=422)


class RemoveAllView(APIView):
    """DELETE /api/organisations/remove-all/<kind>/<parent_id>/
    kind = members (all people of a team), teams (all teams of a project),
           projects (all projects of a house).
    Everything inside is deleted, all or nothing. The parent itself stays."""
    permission_classes = [IsAdminOrAbove]

    def delete(self, request, kind, parent_id):
        if kind == "members":
            parent_kind, parent = "team", Team.objects.filter(id=parent_id).first()
            members = TeamMember.objects.filter(team=parent)
            teams = Team.objects.none()
            projects = Project.objects.none()
            project_ids = []
        elif kind == "teams":
            parent_kind, parent = "project", Project.objects.filter(id=parent_id).first()
            teams = Team.objects.filter(project=parent)
            members = TeamMember.objects.filter(team__in=teams)
            projects = Project.objects.none()
            project_ids = [parent_id]
        elif kind == "projects":
            parent_kind, parent = "organisation", Organisation.objects.filter(id=parent_id).first()
            projects = Project.objects.filter(organisation=parent)
            teams = Team.objects.filter(project__in=projects)
            members = TeamMember.objects.filter(team__in=teams)
            project_ids = list(projects.values_list("id", flat=True))
        else:
            return self.blocked("type must be members, teams or projects")

        if parent is None:
            raise AppError("NOT_FOUND", 404)

        # money is never wiped: any spending stops the whole delete
        if Project.objects.filter(id__in=project_ids).filter(
                Q(actual_paise__gt=0) | Q(committed_paise__gt=0)).exists():
            return self.blocked("A project here has spending, so it cannot be removed.")

        counts = {"members": members.count(), "teams": teams.count(), "projects": projects.count()}
        if sum(counts.values()) == 0:
            return self.blocked("There is nothing to remove.")

        try:
            with transaction.atomic():
                members.delete()    # people first, then teams, then projects
                teams.delete()
                projects.delete()
                log(request, f"{kind}.removed_all", parent_kind, parent_id, {"deleted": counts})
        except ProtectedError:
            return self.blocked("Something here is in use, so it cannot be removed.")

        return Response({"code": "ITEMS_REMOVED", "message": get_message("ITEMS_REMOVED"),
                         "deleted": counts})

    def blocked(self, details):
        return Response({"code": "REMOVE_BLOCKED", "message": get_message("REMOVE_BLOCKED"),
                         "details": details}, status=422)


class UpdateHouseView(APIView):
    """PATCH /api/organisations/update/<house_id>/
    Send only what changes: is_suspended, suspended_reason."""
    permission_classes = [IsAdminOrAbove]

    def patch(self, request, house_id):
        org = Organisation.objects.filter(id=house_id).first()
        if org is None:
            raise AppError("NOT_FOUND", 404)

        data = request.data
        changes = {}   # what changed: {"is_suspended": {"from": False, "to": True}}
        try:
            with transaction.atomic():

                # The suspend switch (true or false only)
                if "is_suspended" in data:
                    if not isinstance(data["is_suspended"], bool):
                        raise ValueError("is_suspended must be true or false.")
                    if data["is_suspended"] != org.is_suspended:
                        changes["is_suspended"] = {"from": org.is_suspended, "to": data["is_suspended"]}
                        org.is_suspended = data["is_suspended"]

                # Suspend needs a reason. Un-suspending clears it.
                if "suspended_reason" in data:
                    org.suspended_reason = str(data["suspended_reason"]).strip()[:300]
                if org.is_suspended and not org.suspended_reason:
                    raise ValueError("Give suspended_reason when suspending.")
                if not org.is_suspended:
                    org.suspended_reason = ""

                if changes or "suspended_reason" in data:
                    org.save()
                    log(request, "house.updated", "organisation", org.id,
                        {"changes": changes, "suspended_reason": org.suspended_reason})

        except ValueError as error:
            return Response({"code": "HOUSE_INVALID", "message": get_message("HOUSE_INVALID"),
                             "details": str(error)}, status=422)

        return Response({"code": "HOUSE_UPDATED", "message": get_message("HOUSE_UPDATED"), "changes": changes})


class AddToHouseView(APIView):
    """POST /api/organisations/add/<house_id>/
    Add projects, teams and people to a house that already exists. Saves all or nothing.
    A project or team with the same name is reused, so you can add a team to an old project."""
    permission_classes = [IsAdminOrAbove]

    def post(self, request, house_id):
        org = Organisation.objects.filter(id=house_id).first()
        if org is None:
            raise AppError("NOT_FOUND", 404)

        counts = {"projects": 0, "teams": 0, "members": 0}   # only NEW things are counted
        try:
            with transaction.atomic():

                for p in request.data.get("projects", []):

                    # Project: use the one with this name in this house, or create it
                    project = Project.objects.filter(organisation=org, name=p["name"]).first()
                    if project is None:
                        if p.get("project_type") not in Project.Type.values:
                            raise ValueError("project_type must be movie, ott_series, ad or other")
                        project = Project.objects.create(
                            organisation=org,
                            name=p["name"],
                            project_type=p["project_type"],
                        )
                        counts["projects"] += 1

                    for t in p.get("teams", []):

                        # Team: use the one with this name in this project, or create it
                        team = Team.objects.filter(project=project, name=t["name"]).first()
                        if team is None:
                            team = Team.objects.create(
                                project=project,
                                name=t["name"],
                                budget_paise=t.get("budget_paise", 0),
                                advance_paise=t.get("advance_paise", 0),
                            )
                            counts["teams"] += 1

                        # People: always added
                        for m in t.get("members", []):
                            TeamMember.objects.create(
                                team=team,
                                name=m["name"],
                                phone=m.get("phone", ""),
                                job_title=m.get("job_title", ""),
                                is_team_head=bool(m.get("is_team_head")),
                            )
                            counts["members"] += 1

                if sum(counts.values()) == 0:
                    raise ValueError("Nothing to add. Send projects, teams or members.")

                log(request, "house.items_added", "organisation", org.id, {"created": counts})

        except KeyError as error:
            return self.bad(f"Missing field: {error.args[0]}")
        except IntegrityError:
            return self.bad("This team already has a team head, or a name is repeated.")
        except (ValueError, TypeError, AttributeError) as error:
            return self.bad(str(error) or "The data is not in the right format.")

        return Response({"code": "ITEMS_ADDED", "message": get_message("ITEMS_ADDED"), "created": counts}, status=201)

    def bad(self, details):
        return Response({"code": "HOUSE_INVALID", "message": get_message("HOUSE_INVALID"),
                         "details": details}, status=422)


class AuditLogListView(APIView):
    """GET /api/organisations/audit-log/?action=house.created&user_id=1  (last 100 lines, superuser only)"""
    permission_classes = [IsSuperUser]

    def get(self, request):
        lines = AuditLog.objects.select_related("user")
        action = request.query_params.get("action")
        user_id = request.query_params.get("user_id")
        if action:
            lines = lines.filter(action=action)
        if user_id and user_id.isdigit():
            lines = lines.filter(user_id=user_id)
        return Response([
            {"id": l.id, "user": l.user.email if l.user else None, "action": l.action,
             "target_type": l.target_type, "target_id": l.target_id,
             "details": l.details, "created_at": l.created_at}
            for l in lines[:100]
        ])