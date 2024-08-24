"""Acá va la logica de las vistas del menu por roles"""
from datetime import datetime
from flask_login import current_user
from script.python.db.consulta_db import buscador_por_key


color = 'light'
dashboard = f'<a class="nav-link text-{color}" href="/dashboard ">Dashboard</a>'
clientes = f'<a class="nav-link text-{color}" href="/clientes">Clientes</a>'
productos = f'<a class="nav-link text-{color}" href="/productos_y_servicios">Productos</a>'
ventas = f'<a class="nav-link text-{color}" href="/ventas">Ventas</a>'
usuarios = f'<a class = "nav-link text-{color}" href = "/usuarios" > Usuarios </a>'

# vistas del menu almacenadas en variables
admin = [dashboard, clientes, productos, ventas]
vendedor = [dashboard, clientes, productos, ventas]
relacion_vista_rol = [[admin], [vendedor]]


def vista_por_rol(rol):
    """Devuelve las vistas del menú asociadas al rol del usuario."""
    rol = int(rol)
    if rol == 0 or rol == 11:
        return admin
    elif rol == 1:
        return vendedor
    elif rol == 10:
        return []
    else:
        return []


def lista_roles(*rol):
    """Devuelve una lista de roles disponibles.

    Roles disponibles:
    0:Admin
    1:Vendedor
    9: super-admin
    10: sin permisos
    11: admin - creador negocio
    
    Status
    0: no activado
    1: activo
    11: activo super-admin (creador de negocio)
    2: desactivado
    3: eliminado
    9: restringido
    """
    return list(rol)
    
def info_sub_menu():
    if current_user:
        fecha_hora_actual = datetime.now()
        fecha = fecha_hora_actual.date()
        fecha_ = fecha.strftime("%d/%m/%Y")
        conexion_db = './database/relacion_usuarios_negocios.db'
        negocio = buscador_por_key(conexion_db, 'relacion_usuario_negocio', 'usuario_id', current_user.id)
        negocio_id = negocio[1]
        datos_negocio = buscador_por_key(conexion_db, 'negocios', 'negocio_id', negocio_id)
        nombre_negocio = datos_negocio[2]
        data ={
            'fecha':fecha_,
            'usuario':current_user.fullname,
            'notificaciones': 0,
            'negocio': nombre_negocio
        }
        return data
    else:
        data ={
            'fecha':'',
            'usuario':'',
            'notificaciones':'',
            'empresa':''
        }
        return data
    

    
