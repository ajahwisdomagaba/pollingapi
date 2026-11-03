from rest_framework import permissions


class IsPollCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS or view.action == 'vote':
            return True
        return obj.creator_id == request.user.id
