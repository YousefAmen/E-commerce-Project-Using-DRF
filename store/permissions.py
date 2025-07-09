from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Only allow access to the owner of the object (no read access for others).
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj.user, "user"):
            return obj.user == request.user
        return False


class IsOrderItemOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.order.user == request.user
