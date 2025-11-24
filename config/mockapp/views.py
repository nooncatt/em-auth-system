from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from mockapp.models import Task
from mockapp.serializers import TaskSerializer
from users.models import User
from users.permissions import AccessRulePermission
from users.services import get_user_from_request

# Две простые ручки:


class TaskListCreateView(ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [AccessRulePermission]
    element_code = "task"  # use in AccessRulePermission

    def get_queryset(self):
        # get current user
        user = get_user_from_request(self.request)

        if not isinstance(user, User) or not user.is_active:
            return Task.objects.none()

        # try to get access rule for this user
        # берём правило доступа тем же способом, что и в permissions
        perm = AccessRulePermission()
        rule = perm._get_rule(user, self)
        if not rule:
            return Task.objects.none()

        qs = Task.objects.select_related("owner")

        # если роль может читать все задачи — отдаём всё
        if rule.can_read_all:
            return qs

        # иначе — только собственные задачи
        return qs.filter(owner=user)

    def perform_create(self, serializer):
        django_request = getattr(self.request, "_request", self.request)

        # пробуем взять пользователя из api_user (куда кладёт JWT-middleware),
        user = getattr(django_request, "api_user", None)

        if not isinstance(user, User) or not user.is_active:
            raise PermissionDenied("Authentication credentials were not provided.")

        serializer.save(owner=user)


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [AccessRulePermission]
    element_code = "task"
    queryset = Task.objects.all()
