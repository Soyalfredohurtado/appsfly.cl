""" estas funciones sirven para manipular las bases de datos del sistema"""
import sqlite3


def verificar_columna_existente(db_name, table_name, column_name):
    """
    Verifica si una columna existe en una tabla específica en una base de datos SQLite3.

    Parámetros:
    - db_name (str): Nombre de la base de datos SQLite3.
    - table_name (str): Nombre de la tabla a verificar.
    - column_name (str): Nombre de la columna a verificar.

    Retorna:
    - bool: True si la columna existe, False en caso contrario.
    """
    with sqlite3.connect(db_name) as conexion:
        cursor = conexion.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columnas = cursor.fetchall()
        for columna in columnas:
            if columna[1] == column_name:
                return True
        return False


def agregar_columna(db_name, table_name, column_name, column_type):
    """
    Agrega una columna a una tabla específica en una base de datos SQLite3.

    Parámetros:
    - db_name (str): Nombre de la base de datos SQLite3.
    - table_name (str): Nombre de la tabla a la que se agregará la columna.
    - column_name (str): Nombre de la columna a agregar.
    - column_type (str): Tipo de datos de la columna a agregar. Puede ser uno de los siguientes:
        - INTEGER: Para almacenar valores enteros.
        - REAL: Para almacenar valores de punto flotante (números decimales).
        - TEXT: Para almacenar cadenas de texto.
        - BLOB: Para almacenar datos binarios (como imágenes, archivos, etc.).
        - NULL: Para almacenar valores nulos.
        - BOOLEAN: SQLite no tiene un tipo de dato booleano nativo,
        pero puedes usar INTEGER y representar 0 como falso y 1 como verdadero.

    Ejemplo de uso:
    agregar_columna("mi_base_de_datos.sql", "clientes", "telefono", "TEXT")
    """
    existe_columna = verificar_columna_existente(
        db_name, table_name, column_name)
    if existe_columna:
        print(f'''
    no se pudo agregar, columna {column_name}, de la tabla {table_name}, db {db_name} Existe
    ''')

    else:

        with sqlite3.connect(db_name) as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
            conexion.commit()
            conexion.close()
            print(f'''
    se agrego con existo la columna {column_name}, tabla {table_name}, db {db_name}''')


agregar_columna("./database/001_77068257-6.sql",
                "cierre_diario_ventas", "cierre_diaro_ventas_numero", "INTEGER")

# Crear logica para recorrer todas las bd
# crear logica para eliminar y corregir
