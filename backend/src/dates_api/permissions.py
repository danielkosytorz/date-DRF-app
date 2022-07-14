from decouple import config
from rest_framework.permissions import BasePermission


class XAPIKEYPermission(BasePermission):
    def has_permission(self, request, view):
        return request.headers.get("X-API-KEY") == config("X_API_KEY")
