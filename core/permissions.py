# core\permissions.py
from rest_framework import permissions
from .services import MembershipService
from .models import SecurityLog


class IsProjectAdminOrReadOnly(permissions.BasePermission):
    """
    Cualquier miembro del proyecto puede leer.
    Solo un admin del proyecto puede modificar (editar/borrar).
    Sirve tanto para Task (obj.project) como para Project (obj).
    """

    def has_object_permission(self, request, view, obj):
        project = obj.project if hasattr(obj, "project") else obj

        # Lectura libre para cualquier miembro del proyecto (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return MembershipService.is_member(request.user, project)

        # Escritura/Modificación (POST, PUT, PATCH, DELETE)
        is_admin = MembershipService.is_admin(request.user, project)

        if not is_admin:
            ip = request.META.get("REMOTE_ADDR")
            
            # Registrar el acceso denegado en la base de datos
            try:
                SecurityLog.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    action="permission_denied",
                    detail=f"Intento no autorizado de {request.method} en proyecto ID {project.id}",
                    ip_address=ip,
                )
            except Exception as e:
                # Si ocurre algún fallo al guardar el log, no interrumpe el flujo principal
                pass

        return is_admin