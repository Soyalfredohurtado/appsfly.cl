"""Acá van las rutas relacionadas con los clientes"""

import sqlite3

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from script.funciones import codigo_unico
from script.python.rutas import validacion_vista_por_rol
from script.python.nav import vista_por_rol, lista_roles, info_sub_menu
from static.style_python.style import style


clientes_bp = Blueprint('clientes', __name__)
usuarios_permitidos = lista_roles(0, 1, 11)


# ========================== TABLE: Clientes  =========================


@clientes_bp.route('')
@login_required
def clientes_table():
    """" vista de los clientes registrados """
    validacion_vista_por_rol(current_user.rol, usuarios_permitidos)
    sub_menu = info_sub_menu()
    nav_rol = vista_por_rol(current_user.rol)
    DB = current_user.conexion_db
    # id para el modal nuevo cliente
    cliente_id = codigo_unico('c')
    # valida a donde se va a redirecionar
    view_redirect = 'tabla_cliente'
    
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM clientes')
        lista_clientes = cursor.fetchall()
        title = 'Clientes'
    return render_template('/clientes/clientes_table.html',
                           title=title, clientes=lista_clientes,
                           nav_rol=nav_rol, cliente_id=cliente_id,
                           view_redirect=view_redirect, style=style,
                           sub_menu=sub_menu)


# ================================ ADD: Clientes  ====================================


@clientes_bp.route('/add/update', methods=['POST'])
@login_required
def cliente_add_update():
    """ recibe por el metodo POST los datos del producto para agregar"""
    DB = current_user.conexion_db
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        cliente_rut = request.form['cliente_rut']
        cliente_nombre = request.form['cliente_nombre']
        cliente_telefono = request.form['cliente_telefono']
        cliente_correo = request.form['cliente_correo']
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute('''INSERT INTO  clientes (cliente_id, cliente_rut,
                           cliente_nombre, cliente_telefono, cliente_correo)
                           VALUES(?, ?, ?, ?, ?)''',
                           (cliente_id, cliente_rut,
                            cliente_nombre, cliente_telefono, cliente_correo))
            conexion.commit()
        flash('Cliente agregado con exito', 'success')
        if request.form['view_redirect'] == 'ventas_tabla':
            return redirect(url_for('ventas.venta_add'))
        else:
            return redirect(url_for('clientes.clientes_table'))
            
# ============================ VIEW: Clientes  =====================================         
@clientes_bp.route('/<id_>')
@login_required
def cliente_view_(id_):
    sub_menu = info_sub_menu()
    DB = current_user.conexion_db
    validacion_vista_por_rol(current_user.rol, usuarios_permitidos)
    nav_rol = vista_por_rol(current_user.rol)
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM clientes')
        lista_clientes = cursor.fetchall()
        
    with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute('''SELECT pago_abono.*, usuarios.usuario_nombre, clientes.cliente_nombre, ventas.venta_folio, forma_de_pago.forma_de_pago_nombre
                            FROM pago_abono
                            INNER JOIN usuarios ON pago_abono.pago_abono_vendedor_id = usuarios.usuario_id
                            INNER JOIN clientes ON pago_abono.pago_abono_cliente_id = clientes.cliente_id
                            INNER JOIN ventas ON pago_abono.pago_abono_venta_id = ventas.venta_id
                            INNER JOIN forma_de_pago ON pago_abono.pago_abono_forma = forma_de_pago.forma_de_pago_id'''
                           )
            pagos_abonos = cursor.fetchall()
            conexion.commit()
    return render_template('/clientes/clientes_view.html', nav_rol=nav_rol, clientes=lista_clientes,  pagos_abonos=pagos_abonos, sub_menu=sub_menu)


# ============================ EDIT: Clientes  =====================================

@clientes_bp.route('/edit/<string:id_>')
@login_required
def cliente_edit(id_):
    """aca edito el producto """
    DB = current_user.conexion_db
    validacion_vista_por_rol(current_user.rol, usuarios_permitidos)
    nav_rol = vista_por_rol(current_user.rol)
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute(
            'SELECT * FROM clientes WHERE cliente_id =?', (id_,))
        cliente = cursor.fetchall()
        title = 'Editar Cliente'
        return render_template('./clientes/cliente_edit.html', cliente=cliente,
                               title=title, nav_rol=nav_rol)


@clientes_bp.route('/edit/update/<string:id_>', methods=['POST'])
def cliente_edit_actualizar(id_):
    """ recibe por el metodo pos los datos del producto para agregar"""
    DB = current_user.conexion_db

    if request.method == 'POST':
        cliente_nombre = request.form['cliente_nombre']
        cliente_telefono = request.form['cliente_telefono']
        cliente_correo = request.form['cliente_correo']
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute("""UPDATE clientes
                            SET cliente_nombre = ?,
                                cliente_telefono = ?,
                                cliente_correo = ?
                            WHERE cliente_id = ?
                        """,
                           (cliente_nombre, cliente_telefono, cliente_correo, id_))
            conexion.commit()
        return redirect(url_for('clientes.clientes_table'))
    else:
        return None


# ============================ DELETE: Clientes  ====================================
@clientes_bp.route('/<string:id_>/delete')
def cliente_delete(id_):
    """ esta ruta elimina clientes"""
    
    if current_user.rol == 0:
        DB = current_user.conexion_db
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                'DELETE FROM clientes WHERE cliente_id= ?', (id_,))
        flash('Cliente Eliminado con exito', 'success')
        return redirect(url_for('clientes.clientes_table'))
    else:
        flash('no tiene permisos para eliminar clientes', 'danger')
        return redirect(url_for('clientes.clientes_table'))
