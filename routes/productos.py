""" aca van las rutas relacionadas con los productos"""
import sqlite3

from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from script.funciones import codigo_unico
from script.python.rutas import validacion_vista_por_rol
from script.python.nav import vista_por_rol, lista_roles,  info_sub_menu
from script.python.db.operaciones_db import sumar_si
from script.python.db.consulta_db import buscador_por_key
from static.style_python.style import style


productos_bp = Blueprint('productos', __name__)


usuarios_permitidos = lista_roles(0, 1, 11)


@productos_bp.route('')
@login_required
def productos_table():
    """ vista productos """
    sub_menu = info_sub_menu()
    DB = current_user.conexion_db
    validacion_vista_por_rol(current_user.rol, usuarios_permitidos)
    nav_rol = vista_por_rol(current_user.rol)
    title = "productos y Servicios"
    producto_id = codigo_unico('p')
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            'SELECT * FROM productos WHERE producto_tipo = ?', ('producto',))
        lista_productos = cursor.fetchall()
        nueva_lista_productos = []
        for producto in lista_productos:
            producto_list = list(producto)
            if producto_list[10]:
                stock_vendidos = 0 - \
                    sumar_si(
                        DB, 'venta_detalle', producto_list[0], 'venta_dt_producto_id', 'venta_dt_cantidad')
                producto_list[5] = stock_vendidos
            else:
                producto_list[5] = '--'

            nueva_lista_productos.append(producto_list)

        cursor.execute(
            'SELECT * FROM productos WHERE producto_tipo = ?', ('servicio',))
        lista_servicios = cursor.fetchall()
        cursor.close()
    title = 'PRODUCTOS Y SERVICIOS'
    return render_template('/productos/productos_table.html',
                           title=title,
                           productos=nueva_lista_productos,
                           servicios=lista_servicios,
                           nav_rol=nav_rol, style=style,
                           producto_id=producto_id,
                           sub_menu=sub_menu)


@productos_bp.route('/add')
@login_required
def producto_add():
    """ vista agregar producto o servicio """
    validacion_vista_por_rol(current_user.rol, usuarios_permitidos)
    nav_rol = vista_por_rol(current_user.rol)
    title = 'Nuevo Producto'
    return render_template('/productos/producto_add.html', title=title,
                           nav_rol=nav_rol)


@productos_bp.route('/add/update', methods=['POST'])
def producto_add_update():
    """ recibe por el metodo pos los datos del producto para agregar"""
    DB = current_user.conexion_db
    if request.method == 'POST':
        producto_id = request.form['productoID']
        # validar que el codigo no est repetido
        producto_codigo = request.form['productoCodigo']
        producto_tipo = request.form['productoTipo']
        producto_nombre = request.form['productoNombre']
        producto_precio = request.form['productoPrecio']
        control_inventario = request.form.get('control_inventario')
        if control_inventario == 1 and producto_tipo != servicio :
            producto_status = 1  # 1 habilitado | 0 deshabilitado
        else:
            producto_status = 0  # 0 deshabilitado
        producto_stock = None
        producto_descripcion = request.form['productoDescripcion']
        fecha = datetime.now().date().isoformat()
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute('''INSERT INTO productos (producto_id, producto_codigo,
                           producto_tipo, producto_nombre,
                           producto_precio, producto_stock,
                           producto_descripcion, producto_status, producto_fecha_creacion, producto_control_inventario)
                           VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (producto_id, producto_codigo, producto_tipo, producto_nombre,
                            producto_precio,
                            producto_stock,
                            producto_descripcion, producto_status, fecha, control_inventario))
            conexion.commit()
        success_mensage = 'agregado'
        flash(success_mensage)
        return redirect(url_for('productos.productos_table'))

# ============================ DELETE: productos y servicios ===================


@productos_bp.route('/delete/<string:id_>')
@login_required
def producto_delete(id_):
    """ explicación  """
    DB = current_user.conexion_db
    validacion_vista_por_rol(current_user.rol, usuarios_permitidos)
    tiene_movimientos = buscador_por_key(DB, 'venta_detalle', 'venta_dt_producto_id', id_)
    if tiene_movimientos:
        flash('Producto no pueder ser eliminado, tiene movimientos en el inventario')
        return redirect(url_for('productos.productos_table'))
    else:
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                'DELETE FROM productos WHERE producto_id = ?', (id_,))
        flash('Producto eliminado con exito')
        return redirect(url_for('productos.productos_table'))
    


# ============================ EDIT: productos y servicios ====================

@productos_bp.route('/edit/<string:id_>')
@login_required
def producto_edit(id_):
    """aca edito el producto """
    validacion_vista_por_rol(current_user.rol, usuarios_permitidos)
    nav_rol = vista_por_rol(current_user.rol)
    with sqlite3.connect('./database/001_77068257-6.sql') as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM productos WHERE producto_id =?', (id_,))
        producto = cursor.fetchall()
        title = 'Editar Producto/Servicio'
        return render_template('./productos/producto_edit.html', producto=producto,
                               nav_rol=nav_rol, title=title)


@productos_bp.route('/edit/update/<string:id_>',
                    methods=['POST'])
@login_required
def producto_edit_actualizar(id_):
    """ recibe por el metodo pos los datos del producto para agregar"""
    if request.method == 'POST':
        producto_nombre = request.form['producto_nombre']
        producto_precio = request.form['producto_precio']
        producto_descripcion = request.form['producto_descripcion']
        with sqlite3.connect('./database/001_77068257-6.sql') as conexion:
            cursor = conexion.cursor()
            cursor.execute("""UPDATE productos
                            SET producto_nombre = ?,
                                producto_precio = ?,
                                producto_descripcion = ?
                            WHERE producto_id = ?
                        """,
                           (producto_nombre, producto_precio,
                            producto_descripcion, id_))
            conexion.commit()
        return redirect(url_for('productos.productos_table'))


# ============================ VIEW: productos y servicios ===================
@productos_bp.route('/<string:id_p>')
@login_required
def prodcuto_view(id_p):
    """ Esta ruta lleva a la vista del producto en detalle por medio del id"""
    validacion_vista_por_rol(current_user.rol, usuarios_permitidos)
    nav_rol = vista_por_rol(current_user.rol)
    title = 'Vista Producto'  # aca puede ser producto o servici
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM productos WHERE producto_id =?', (id_p,))
        producto = cursor.fetchall()
        return render_template('./productos/producto_view.html', producto=producto,
                               nav_rol=nav_rol, title=title)
