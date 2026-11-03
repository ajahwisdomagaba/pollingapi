from rest_framework import permissions


class IsPollCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Anyone who is logged in can look at a poll and vote.
        # Only the person who made the poll can change, close, or delete it.
        if request.method in permissions.SAFE_METHODS or view.action == 'vote':
            return True
        return obj.creator_id == request.user.id
