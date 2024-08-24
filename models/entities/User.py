""" aca va la clase User """
from flask_login import UserMixin
import sqlite3

from werkzeug.security import check_password_hash


class User(UserMixin):
    """descripcion """

    def __init__(self, user_id, email, password, rol, fullname, conexion_db):
        """descripcion"""
        
        with sqlite3.connect('./database/relacion_usuarios_negocios.db') as conexion:
            cursor = conexion.cursor()
            cursor.execute(f'SELECT * FROM relacion_usuario_negocio WHERE usuario_id = ?', (user_id, ))
            relacion_usuario_negocio = cursor.fetchall()
         
        dato_base = ''
        usuario_rol = 9
        for dato in relacion_usuario_negocio:
            dato_ = list(dato)
            if len(dato_) > 0:
                dato_base = dato_[4]
                usuario_rol = dato_[2]
                    
             
        self.id = user_id
        self.email = email
        self.password = password
        self.rol = usuario_rol
        self.fullname = fullname
        self.conexion_db = dato_base

    @classmethod
    def check_password(cls, hashed_password, password):
        """ verifica si son iguales las contraseñas y devuelve true o false"""
        return check_password_hash(hashed_password, password)
