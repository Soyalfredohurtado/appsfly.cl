""" Código para crar db cuando se crea un negocio nuevo """

import sqlite3
import os
from flask import flash

def creacion_db_negocio(nombre_nueva_db):
    """ Crear la bd del un negocio, copiando la bd original.
    db_original: ruta original de la db 
    nombre_nueva_db: como se va a llamar la nueva db
    """
    # Paso 1: Obtener la estructura de la base de datos actual
    with sqlite3.connect('./database/negocios/modelos/modelo_basico_optica.sql') as conexion:
        cursor = conexion.cursor()
        # Obtener los nombres de las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        # Almacenar el código que se va a ejecutar
        script_sql = ''
        for tabla in tablas:
            tabla_nombre = tabla[0]
            # Obtener información detallada sobre las columnas de la tabla actual
            cursor.execute(f"PRAGMA table_info({tabla_nombre})")
            columnas = cursor.fetchall()
            script_sql += f"\n\n-- Definición de la tabla {tabla_nombre}\n"
            script_sql += f"CREATE TABLE {tabla_nombre} (\n"
            for columna in columnas:
                nombre_columna = columna[1]
                tipo_dato = columna[2]
                script_sql += f"    {nombre_columna} {tipo_dato},\n"
            script_sql = script_sql.rstrip(',\n') + "\n);"
    # Paso 2: Ejecutar el script SQL en la nueva base de datos
    with sqlite3.connect(nombre_nueva_db) as conexion_nueva:
        cursor_nueva = conexion_nueva.cursor()
        # Ejecutar el script SQL almacenado en script_sql
        cursor_nueva.executescript(script_sql)
    flash('db creada exitosamente', 'succes')