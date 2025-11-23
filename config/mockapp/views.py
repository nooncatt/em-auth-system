from django.shortcuts import render
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from mockapp.models import Task
from mockapp.serializers import TaskSerializer
from users.models import User, BusinessElement, AccessRule
from users.permissions import AccessRulePermission


# Две простые ручки:


class TaskListCreateView(ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [AccessRulePermission]
    element_code = "task"  # will use in permission

    def get_queryset(self):
        django_request = getattr(self.request, "_request", self.request)
        user = getattr(django_request, "user", None)

        if not isinstance(user, User) or not user.is_active:
            return Task.objects.none()

        try:
            element = BusinessElement.objects.get(code="task")
            rule = AccessRule.objects.get(role=user.role, element=element)
        except (BusinessElement.DoesNotExist, AccessRule.DoesNotExist):
            return Task.objects.none()

        if rule.can_read_all:
            return Task.objects.all()

        return Task.objects.filter(owner=user)

    def perform_create(self, serializer):
        django_request = getattr(self.request, "_request", self.request)

        # СНАЧАЛА пробуем взять пользователя из api_user (куда кладёт JWT-middleware),
        # если по каким-то причинам его нет — падаем с 403, чтобы не было 500.
        user = getattr(django_request, "api_user", None)

        if not isinstance(user, User) or not user.is_active:
            raise PermissionDenied("Authentication credentials were not provided.")

        serializer.save(owner=user)


class TaskDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [AccessRulePermission]
    element_code = "task"
    queryset = Task.objects.all()
