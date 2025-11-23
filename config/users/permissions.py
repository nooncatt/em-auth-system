from rest_framework.permissions import BasePermission
from users.models import User, BusinessElement, AccessRule
from users.services import get_user_from_request


class AccessRulePermission(BasePermission):
    def _get_user(self, request):
        user = get_user_from_request(request)
        if not isinstance(user, User) or not user.is_active:
            return None
        return user

    def _get_rule(self, user, view):
        element_code = getattr(view, "element_code", None)
        if not element_code:
            return None

        try:
            element = BusinessElement.objects.get(code=element_code)
            return AccessRule.objects.get(role=user.role, element=element)
        except (BusinessElement.DoesNotExist, AccessRule.DoesNotExist):
            return None

    # GLOBAL PERMISSIONS
    def has_permission(self, request, view):
        user = self._get_user(request)
        if not user:
            return False

        rule = self._get_rule(user, view)
        if not rule:
            return False

        method = request.method.upper()

        if method in ("GET", "HEAD", "OPTIONS"):
            return rule.can_read or rule.can_read_all
        if method == "POST":
            return rule.can_create
        if method in ("PUT", "PATCH"):
            return rule.can_update or rule.can_update_all
        if method == "DELETE":
            return rule.can_delete or rule.can_delete_all

        return False

    # PERMISSIONS on the OBJECT level (detail)
    def has_object_permission(self, request, view, obj):
        user = self._get_user(request)
        if not user:
            return False

        rule = self._get_rule(user, view)
        if not rule:
            return False

        method = request.method.upper()

        # firstly check *_all rules
        if method in ("GET", "HEAD", "OPTIONS") and rule.can_read_all:
            return True
        if method in ("PUT", "PATCH") and rule.can_update_all:
            return True
        if method == "DELETE" and rule.can_delete_all:
            return True

        # or check «simple» rules and it's owner
        owner = getattr(obj, "owner", None)

        if method in ("GET", "HEAD", "OPTIONS"):
            return rule.can_read and owner == user
        if method in ("PUT", "PATCH"):
            return rule.can_update and owner == user
        if method == "DELETE":
            return rule.can_delete and owner == user

        return False
