import sqlite3
from script.funciones import codigo_unico

def eliminar_por_id(db, table, column, key, usuario_id, autorizados=None):
    """
    Elimina datos de una tabla en la base de datos y registra la eliminacion.

    Parametros:
    db (str): Nombre de la base de datos.
    table (str): Nombre de la tabla en la base de datos.
    column (str): Nombre de la columna en la tabla.
    key (str): Valor de la clave primaria a comparar.
    usuario_id (str): ID del usuario que realiza la eliminacion.
    autorizados (list, opcional): Lista de roles autorizados para realizar la eliminacion.
    
    Returns:
    None
    """

    # Recuperar los datos que se van a eliminar (si es necesario)
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE {column} = ?", (key,))
        datos_lista = cursor.fetchone()
        
        # Eliminar los datos
        cursor.execute(f"DELETE FROM {table} WHERE {column} = ?", (key,))
        conexion.commit()
        
    detalle = f'db:{db}, tabla:{table}, id:{key}'
    lista = [datos_lista] if datos_lista else []  # Asegurarse de pasar una lista

    registro_delete(db, lista, detalle, usuario_id)


def registro_delete(db, datos_lista, detalle, usuario_id):
    """
    Registra los datos eliminados para poder recuperarlos.

    Args:
    db (str): Nombre de la base de datos.
    datos_lista (list): Lista con los datos eliminados.
    detalle (str): Detalle de la eliminacion, por ejemplo, "venta eliminada".
    usuario_id (str): ID del usuario que realizo la eliminacion.
    
    Returns:
    None
    """
    registro_delete_id = codigo_unico('delete')
    lista = str(datos_lista)  # Convertimos la lista a string para almacenarla en la base de datos
    
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO registro_datos_eliminados 
            (registro_delete_id, registro_delete_lista, registro_delete_detalle, registro_delete_usuario_id)
            VALUES (?, ?, ?, ?)
        """, (registro_delete_id, lista, detalle, usuario_id))
        conexion.commit()
