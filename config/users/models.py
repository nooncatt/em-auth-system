from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)


class User(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    role_id = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # todo: (soft delete)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BusinessElement(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)


class AccessRule(models.Model):
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    element = models.ForeignKey(BusinessElement, on_delete=models.PROTECT)
    can_read = models.BooleanField(default=False)
    can_read_all = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_update_all = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_delete_all = models.BooleanField(default=False)
