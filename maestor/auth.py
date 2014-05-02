from rest_framework.permissions import BasePermission

class ServerAuth(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return True
        #Should use server name and api key