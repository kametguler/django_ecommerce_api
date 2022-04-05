from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class CartOwnerOrNotAccess(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if obj.customer == request.user:
            return True


class IsAdminUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True


class CheckoutFor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.customer == request.user:
            return True
