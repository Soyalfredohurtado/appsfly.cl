""" funciones para realizar operaciones matematicas en la db"""

import sqlite3


def sumar_si(db, tabla, condicion, columna_condicion, columna_a_sumar):
    """ 
    Suma los valores de la columna si se cumple una condición.

    Args:
    db: Ruta de la base de datos SQLite.
    tabla: Nombre de la tabla.
    condicion: Condición que debe cumplir la columna de la condición.
    columna_condicion: Nombre de la columna de la condición.
    columna_a_sumar: Nombre de la columna a sumar.
    """
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            f"SELECT SUM({columna_a_sumar}) FROM {tabla} WHERE {columna_condicion} = '{condicion}'"
        )
        resultado = cursor.fetchone()[0]
        return resultado if resultado is not None else 0


def sumar_si_conjunto(db, tabla, columna_a_sumar, condiciones):
    """ 
    Suma los valores de la columna si se cumple una condición.
    Args:
    db: Ruta de la base de datos SQLite.
    tabla: Nombre de la tabla.
    columna_a_sumar: Nombre de la columna a sumar.
    condiciones: debe se una lista de lista de columna y condcion
    """
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            f"""SELECT SUM({columna_a_sumar}) FROM {tabla} WHERE {condiciones[0][0]} =
            '{condiciones[0][1]}' AND  {condiciones[1][0]} = '{condiciones[1][1]}'""")
        resultado = cursor.fetchone()[0]
        return resultado if resultado is not None else 0
