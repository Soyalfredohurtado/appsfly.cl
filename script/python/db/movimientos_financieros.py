"""codígos para relacionados momivimentos financieros y db"""
import sqlite3

from datetime import datetime
from script.funciones import codigo_unico, numero_de_control
from script.python.db.operaciones_db import sumar_si


def registrar_movimiento_efectivo(db, origen_id, origen, tipo, monto, usuario):
    """Registra los movimientos de efectivo

    Parametros
    db(str): ruta de la basedata
    origen(str) : descripción del origen del movimiento
    tipo(bool): 0-entradao | 1-salida
    monto(int): monto del movimiento
    usuario(str): id usuario
    """
    movimiento_efectivo_id = codigo_unico('me')
    numero_control = numero_de_control(db, 'movimientos_efectivo')
    saldo = None


    fecha_hora_actual = datetime.now()
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute('''INSERT INTO movimientos_efectivo (movimiento_efectivo_id,
                       movimiento_efectivo_numero_control, movimiento_efectivo_tipo,
                       movimiento_efectivo_origen_id,
                       movimiento_efectivo_origen, movimiento_efectivo_monto,
                       movimiento_efectivo_saldo, movimiento_efectivo_data_registro,
                       movimiento_efectivo_usuario_id)
                           VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (movimiento_efectivo_id, numero_control,
                        tipo, origen_id, origen, monto, saldo, fecha_hora_actual, usuario))
        conexion.commit()
