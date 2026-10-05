from rest_framework.permissions import BasePermission


class IsInspector(BasePermission):
    message = "Only Inspectors can perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.groups.filter(
            name="Inspector"
        ).exists()


class IsTeamLead(BasePermission):
    message = "Only Team Leads can perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.groups.filter(
            name="Team Lead"
        ).exists()


class IsAdmin(BasePermission):
    message = "Only Admins can perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.groups.filter(
            name="Admin"
        ).exists()


class IsInspectorTeamLeadAdmin(BasePermission):
    message = (
        "Only Inspectors, Team Leads, or Admins "
        "can perform this action."
    )

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.groups.filter(
            name__in=[
                "Inspector",
                "Team Lead",
                "Admin",
            ]
        ).exists()