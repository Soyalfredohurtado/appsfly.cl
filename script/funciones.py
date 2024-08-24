""" en este archivo almacenamos todas las funciones generales a plclaves a todo el codigo"""
import uuid
import sqlite3


def codigo_unico(letra):
    """ esta funcion creda un codido unico

    recibe como argumento una lentr 

    p para productos
    c clientyes
    u usuarios
    pa para pagos y abonos

    """
    letra_ = letra
    uuid_value = str(uuid.uuid4())
    codigo_key = uuid_value[:10].replace('-', '')
    return letra_ + codigo_key


def contar_registros_ultima_venta(db):
    """cuentas cuantas ventas hay registrada en la base de dato """
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM ventas")
        cantidad_registros = cursor.fetchone()[0]

    return cantidad_registros


def numero_venta_acutual(db):
    """devuelve el numero de venta actual"""
    return int(contar_registros_ultima_venta(db) + 1)


def calcular_venta_total(db, numero_venta_):
    """suma el total de detalle de las ventas donde coincida el numero de venta"""
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT SUM(venta_dt_total) FROM ventas_detalle WHERE venta_dt_venta_id = ?",
                       (numero_venta_,))
        total_venta = cursor.fetchone()[0]
    return total_venta if total_venta else 0


def numero_de_control(db, table):
    """calcula el ultimo registro, debe ingresar: base datos, nombre tabla"""
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        cantidad_registros = cursor.fetchone()[0]
        return int(cantidad_registros) + 1
