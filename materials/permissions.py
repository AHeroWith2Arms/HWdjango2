from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Модераторы').exists()


class IsOwnerOrModerator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.groups.filter(name='Модераторы').exists()
        action = getattr(view, 'action', None)
        
        if not action:
            if request.method in ['PUT', 'PATCH']:
                action = 'update'
            elif request.method == 'DELETE':
                action = 'destroy'
            elif request.method == 'GET':
                action = 'retrieve'
            elif request.method == 'POST':
                action = 'create'
        
        if is_moderator:
            if action in ['update', 'partial_update', 'retrieve', 'list']:
                return True
            if action in ['create', 'destroy']:
                return False
        
        if action == 'create':
            return True
        
        return obj.owner == request.user


class IsOwnerOrModeratorReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_moderator = request.user.groups.filter(name='Модераторы').exists()
        action = getattr(view, 'action', None)
        
        if not action:
            if request.method in ['PUT', 'PATCH']:
                action = 'update'
            elif request.method == 'DELETE':
                action = 'destroy'
            elif request.method == 'GET':
                action = 'retrieve'
            elif request.method == 'POST':
                action = 'create'
        
        if is_moderator:
            if action in ['update', 'partial_update', 'retrieve', 'list']:
                return True
            if action in ['create', 'destroy']:
                return False
        
        if action in ['retrieve', 'list']:
            return True
        
        if action == 'create':
            return True
        
        return obj.owner == request.user