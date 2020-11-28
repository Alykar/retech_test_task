from rest_framework import permissions


class IsMemberOrForbid(permissions.BasePermission):
    """
    Use this only for Organization model permission checks.
    It allows refactor data only to it's owner,
    and reading data only to Organizations.employees or Organization.owner.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # filter, not get, yep, cos i need to now if user belong to obj.employees, not deal with errors if it don't
            return obj.owner == request.user or obj.employees.filter(id=request.user.id).exists()
        # modifications allowed only to  org's creator (das 'owner')
        return obj.owner == request.user