""" funciones para consulta en la db"""
import sqlite3

from script.python.db.operaciones_db import sumar_si


def datos_tabla_(db, table, key=False, id_table='', ordenar=False):
    """Devuelve una lista con la tabla de datos de la bd con sqlite3.
    Parámetros:
    db(str): ruta base de datos
    table(str): nombre de la tabla en la base de datos
    key(str): si se desea agregar los datos de una tabla con un valor específico
    id_table(str): nombre de la columna donde se va comparar si existe la key
    ordenar(str): nombre de la columna por la cual se va a ordenar
    """
    # Si el parámetro key es verdadero, devuelve los datos de la tabla para la clave especificada.
    if key:
        with sqlite3.connect(db) as conexion:
            cursor = conexion.cursor()
            if ordenar:
                cursor.execute(f'SELECT * FROM {table} WHERE {id_table} = ? ORDER BY {ordenar}', (key, ))
            else:
                cursor.execute(f'SELECT * FROM {table} WHERE {id_table} = ?', (key, ))
            data = cursor.fetchall()

    # Si el parámetro key es falso, devuelve todos los datos de la tabla.
    else:
        with sqlite3.connect(db) as conexion:
            cursor = conexion.cursor()
            if ordenar:
                cursor.execute(f'SELECT * FROM {table} ORDER BY {ordenar}')
            else:
                cursor.execute(f'SELECT * FROM {table}')
            data = cursor.fetchall()

    return data

def datos_tabla_todos(db, table):
    """ devuelve los datos de una tabla.

    Parámetros:
        db: nombre db
        table: nombre de la tabla

    Retorna:
        list: Una lista de tuplas que representan los datos de la tabla.
    """
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute(f'SELECT * FROM {table}')
        data = cursor.fetchall()
        if data:
            return data
        else:
            return []

def buscador_por_key(db, table, id_table, key):
    """Busca en la DB por su key
    Parámetros:
        db: nombre db
        table: nombre de la tabla
        id_table: id a buscar en la tabla
        key: clave
    """
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute(f'SELECT * FROM {table} WHERE {id_table} = ?', (key,))
        data = cursor.fetchall()
        if data:
            return data[0]
        else:
            return []  # Manejar el caso en que no se encuentre ninguna fila

def datos_tabla(db, table, columna, key):
    """ devuelve los datos de una tabla que coincide con su key 
    Args:
        db: nombre db
        table: nombre de la tabla
        columna: columna donde se buscara la key
        key: clave
    """
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute(f'SELECT * FROM {table} WHERE {columna} =?', (key,))
        data = cursor.fetchall()
        if data:
            return data
        else:
            return []

def contar_por_key(db, table, columna, key):
    """Cuenta cuántas veces está un dato en una tabla que coincide con su key.

    Args:
        db (str): Nombre de la base de datos.
        table (str): Nombre de la tabla.
        columna (str): Nombre de la columna donde se buscará la key.
        key: Valor de la clave a buscar.

    Returns:
        int: Número de veces que aparece la key en la columna especificada.
    """
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            f'SELECT COUNT(*) FROM {table} WHERE {columna} = ?', (key,))
        data = cursor.fetchone()
        if data:
            return data[0]
        else:
            return 0
            
def existe_valor_id(db, table, column, value):
    # Conectarse a la base de datos
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} = ?", (value,))
        resultado = cursor.fetchone()[0]
        
    # Devolver True si el valor existe, False si no existe
    return resultado > 0

def total_abono_cxc(db, data):
    """ busca de la lista venta su monto sumando el detalle de la venta y sus abonos 
    sumando el detalle de pagos y abonos y luego calcula la cuenta por cobrar.
    agrega a la lista total , abono, cxc y text-dander(formato para los que posean deuda)"""
    ventas = data
    nueva_lista = []
    for venta in ventas:
        lista_venta_dt = list(venta)
        total = sumar_si(db, 'venta_detalle',
                         venta[0], 'venta_dt_venta_id', 'venta_dt_total')
        abono = sumar_si(db, 'pago_abono',
                         venta[0], 'pago_abono_venta_id', 'pago_abono_monto')
        cxc = total - abono
        estado = 'btn-danger text-danger' if cxc > 10 else ''
        lista_venta_dt.extend([total, abono, cxc, estado])
        nueva_lista.append(lista_venta_dt)
    return nueva_lista

def ventas_generales(db):
    """ busca en la tabla ventas de la db totas las ventas y crea una lista"""
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""SELECT ventas.*, clientes.cliente_nombre
                FROM ventas
                INNER JOIN clientes ON ventas.venta_cliente_id = clientes.cliente_id""")
        ventas = cursor.fetchall()
        lista_ventas = []
        for venta in ventas:
            db_negocios_usuarios ='./database/relacion_usuarios_negocios.db'
            vendedor = buscador_por_key(db_negocios_usuarios, 'usuarios', 'usuario_id', venta[5])
            nombre_vendedor = vendedor[3]
            ventas_ = list(venta)
            ventas_[5] = nombre_vendedor
            lista_ventas.append(ventas_)

        return lista_ventas

def ventas_generales_ordenada(db):
    ventas = ventas_generales(db)
    ventas_ordenadas = total_abono_cxc(db, ventas)
    ventas_ordenadas.reverse()
    return ventas_ordenadas
