import sqlite3
from datetime import datetime
from flask import flash
from script.python.db.consulta_db import contar_por_key

def create_usuario(db, usuario_id, rut, nombre, rol, status, password, correo):
    """Agrega usuarios a la base de datos.
    
    db (str): Ruta de la base de datos.
    usuario_id (str): ID de usuario(unico).
    rut (str): RUT del usuario(unico).
    nombre (str): Nombre y apellido del usuario.
    rol (str): Rol del usuario.
    status (str): Estado del usuario.
    password (str): Contraseña hasheada.
    correo (str): Correo electrónico del usuario.
    """
    try:
        existe_usuario = contar_por_key(db, 'usuarios', 'usuario_rut', rut)
        if existe_usuario: 
            flash('Usuario se encuentra registrado', 'warning')
            

        else:
            with sqlite3.connect(db) as conexion:
                cursor = conexion.cursor()
                cursor.execute('''INSERT INTO usuarios (usuario_id, usuario_rut, usuario_nombre,
                                   usuario_rol, usuario_status, usuario_password, usuario_correo)
                                   VALUES(?, ?, ?, ?, ?, ?, ?)''',
                                   (usuario_id, rut, nombre, rol, status, password, correo))
                conexion.commit()
            flash(f'Usuario {nombre} agregado con éxito')
    except sqlite3.Error as e:
        flash(f'Error al agregar usuario: {e}')


    