""" aca nos estamos conectado a la bd"""
import sqlite3

try:
    with sqlite3.connect('./database/001_77068257-6.sql') as conexion:
        print(conexion)
    # La conexión se cerrará automáticamente al salir del bloque "with"

except ImportError:
    print('Error de lectura de la base de datos')
