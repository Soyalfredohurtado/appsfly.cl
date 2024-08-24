"""aca van todas las validaciones que se aplican a las rutas """
from flask import flash, redirect, url_for


def validacion_vista_por_rol(usuario_rol, rol_permitido):
    """Valida que el rol del usuiario este autorizado para ingresar a la vista.
    Parámetros:
    (int)usurio_rol : numero de rol de usuario.
    (list)rol_permitido : lista de los roles permitidos

    roles:
    0 admin
    1 vendedor
    """
    usuario_rol = int(usuario_rol)
    if usuario_rol in rol_permitido:
        return True
    else:
        flash(f'no tiene permiso para acceder' , 'danger')
        return False
