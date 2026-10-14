from django.db.models import Count
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import AppError
from core.messages import get_message
from core.permissions import IsSuperUser
from .excel_import import import_excel
from .models import Organisation, Plan, Project, Team, TeamMember
from .serializers import HouseSerializer
from django.db import IntegrityError, connection, transaction
from django.db.models import ProtectedError

class HouseListView(APIView):
    """GET: all production houses with their projects (the 'Production houses' page)."""
    permission_classes = [IsSuperUser]

    def get(self, request):
        houses = (Organisation.objects.select_related("plan")
                  .prefetch_related("projects__teams")
                  .annotate(user_count=Count("users", distinct=True))
                  .order_by("name"))
        return Response(HouseSerializer(houses, many=True).data)


class UploadView(APIView):
    """POST: form field 'file' = the .xlsx. Saves everything, or nothing if any row is wrong."""
    permission_classes = [IsSuperUser]
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get("file")
        if not file or not file.name.lower().endswith(".xlsx"):
            raise AppError("FILE_BAD", 400)
        try:
            counts = import_excel(file)
        except ValueError as error:
            # same shape as the other errors: code, message, details (details says which row)
            return Response({"code": "UPLOAD_HAS_ERRORS", "message": get_message("UPLOAD_HAS_ERRORS"),
                             "details": str(error)}, status=422)
        return Response({"code": "UPLOAD_SAVED", "message": get_message("UPLOAD_SAVED"), "created": counts}, status=201)

class CreateHouseView(APIView):
    """POST: one JSON with the house, its projects, teams and people. Saves all or nothing."""
    permission_classes = [IsSuperUser]

    def post(self, request):
        data = request.data   # the JSON from the frontend, as a Python dictionary
        try:
            # "atomic" = if any line below fails, everything saved so far is undone
            with transaction.atomic():

                # 1. Plan: find it by name. If it is not there, create it.
                plan = Plan.objects.filter(name=data["plan_name"]).first()   # SELECT ... WHERE name = ...
                if plan is None:
                    plan = Plan.objects.create(                              # INSERT a new plan
                        name=data["plan_name"],
                        price_paise=data.get("plan_price_paise", 0),         # 0 if the frontend did not send it
                    )

                # 2. Production house
                org = Organisation.objects.create(                           # INSERT a new house
                    name=data["name"],                                       # data["x"] = required, error if missing
                    plan=plan,
                    whatsapp_alerts=bool(data.get("whatsapp_alerts")),       # data.get("x") = optional, empty if missing
                    bill_ocr=bool(data.get("bill_ocr")),
                    tally_export=bool(data.get("tally_export")),
                    multi_project_dashboard=bool(data.get("multi_project_dashboard")),
                )

                # 3. Projects of this house
                for p in data.get("projects", []):
                    if p["project_type"] not in Project.Type.values:
                        raise ValueError("project_type must be movie, ott_series, ad or other")
                    project = Project.objects.create(                        # INSERT a new project
                        organisation=org,                                    # links the project to the house
                        name=p["name"],
                        project_type=p["project_type"],
                    )

                    # 4. Teams of this project
                    for t in p.get("teams", []):
                        team = Team.objects.create(                          # INSERT a new team
                            project=project,                                 # links the team to the project
                            name=t["name"],
                            budget_paise=t.get("budget_paise", 0),
                            advance_paise=t.get("advance_paise", 0),
                        )

                        # 5. People of this team
                        for m in t.get("members", []):
                            TeamMember.objects.create(                       # INSERT a new person
                                team=team,                                   # links the person to the team
                                name=m["name"],
                                phone=m.get("phone", ""),
                                job_title=m.get("job_title", ""),
                                is_team_head=bool(m.get("is_team_head")),
                            )

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
    """DELETE /api/organisations/remove/<type>/<id>/  where type = plan, organisation, project, team or member"""
    permission_classes = [IsSuperUser]

    def delete(self, request, kind, item_id):
        tables = {"plan": Plan, "organisation": Organisation, "project": Project,
                  "team": Team, "member": TeamMember}
        if kind not in tables:
            return self.blocked("type must be plan, organisation, project, team or member")

        item = tables[kind].objects.filter(id=item_id).first()   # SELECT ... WHERE id = ...
        if item is None:
            raise AppError("NOT_FOUND", 404)

        if kind == "member":
            # never delete a person: switch them off
            item.is_active = False
            item.save(update_fields=["is_active"])
            return self.removed()

        if kind == "project" and (item.actual_paise or item.committed_paise):
            return self.blocked("This project has spending, so it cannot be removed.")

        try:
            item.delete()
        except ProtectedError:
            return self.blocked("It has something inside it (or is in use). Remove that first.")
        return self.removed()

    def removed(self):
        return Response({"code": "MEMBER_SWITCHED_OFF", "message": get_message("MEMBER_SWITCHED_OFF")})

    def blocked(self, details):
        return Response({"code": "REMOVE_BLOCKED", "message": get_message("REMOVE_BLOCKED"),
                         "details": details}, status=422)
