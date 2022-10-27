from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsDoctor(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_doctor:
            return bool(request.method in SAFE_METHODS)
        return bool(request.user and request.user.is_authenticated)
