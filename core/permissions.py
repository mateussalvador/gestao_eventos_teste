from rest_framework.permissions import BasePermission

class IsOrganizadorOrReadOnly(BasePermission):
    """
    Permite leitura para todos, mas escrita apenas para organizadores.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user.is_authenticated and request.user.tipo == 'organizador'

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user.is_authenticated and request.user.tipo == 'organizador'

class IsResponsavelOrReadOnly(BasePermission):
    """
    Permite leitura para todos, mas escrita apenas para o responsável da atividade.
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.responsavel == request.user