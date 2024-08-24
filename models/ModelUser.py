""" Descripción """
import sqlite3

from werkzeug.security import check_password_hash

from flask import request

from models.entities.User import User


class ModelUser():
    """ Descripción """

    @classmethod
    def login(cls, db, user):
        """ descripcion """
        user_email = request.form['usuario_correo']
        user_password = request.form['usuario_password']
        with sqlite3.connect(db) as conexion:
            cursor = conexion.cursor()
            cursor.execute("""SELECT usuario_id, usuario_correo, usuario_password,
                           usuario_rol, usuario_nombre
                           FROM usuarios WHERE usuario_correo=?""",
                           (user_email,))
            row = cursor.fetchone()
        if row is not None:
            user = User(row[0], row[1], check_password_hash(row[2], user_password),
                        row[3], row[4], './database/negocios/001_770682576.sql')
            return user
        else:

            return None

    @classmethod
    def get_by_id(cls, db, id_):
        """ Trabajar con excepciones"""
        with sqlite3.connect(db) as conexion:
            cursor = conexion.cursor()
            cursor.execute("""SELECT usuario_id, usuario_correo, usuario_password,
                           usuario_rol, usuario_nombre, usuario_conexion_db
                            FROM usuarios WHERE usuario_id=?""", (id_,))
            row = cursor.fetchone()
            if row is not None:
                return User(row[0], row[1], None, row[3], row[4], './database/negocios/001_770682576.sql' )#row[5]
            else:
                return None
