""" aca van las rutas relacionadas con las ventas """
import sqlite3

from datetime import datetime
from flask_login import current_user, login_required
from flask import Blueprint, flash, render_template, request, jsonify, redirect, url_for
from script.funciones import codigo_unico, numero_venta_acutual,  numero_de_control
from script.python.db.consulta_db import buscador_por_key, contar_por_key, ventas_generales_ordenada, existe_valor_id
from script.python.db.operaciones_db import sumar_si
from script.python.db.movimientos_financieros import registrar_movimiento_efectivo
from script.python.db.delete_db import eliminar_por_id
from static.style_python.style import style
from script.python.nav import vista_por_rol, info_sub_menu


ventas_bp = Blueprint('ventas', __name__)


@ventas_bp.route('/')
@login_required
def ventas_table():
    """ vista ventas """
    nav_rol = vista_por_rol(current_user.rol)
    sub_menu = info_sub_menu()
    DB = current_user.conexion_db
    lista_venta = ventas_generales_ordenada(DB)
    title = "Venta General"
    return render_template('/ventas/ventas_table.html', title=title, ventas=lista_venta, sub_menu = sub_menu, nav_rol=nav_rol)


@ventas_bp.route('add')
@login_required
def venta_add():
    """" vista """
    nav_rol = vista_por_rol(current_user.rol)
    DB = current_user.conexion_db
    fecha_hora_actual = datetime.now()
    fecha_actual = fecha_hora_actual.date()
    fecha = fecha_hora_actual.date().strftime("%d/%m%Y")
    hora = fecha_hora_actual.time()
    title = 'AppsFly | NUEVA VENTA'
    venta_id = codigo_unico('v')
    cliente_id = codigo_unico('c')
    # valida a donde se va a redirecionar
    view_redirect = 'ventas_tabla'

    cierre_diario_actual = contar_por_key(DB, 'cierre_diario_ventas',
                                          'cierre_diario_fecha', fecha_actual)
    if cierre_diario_actual > 0:
        flash('Caja Cerrada', 'danger')
        return redirect(url_for('ventas.ventas_table'))

    else:
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute('SELECT * FROM productos')
            productos = cursor.fetchall()
            cursor.execute('SELECT * FROM clientes')
            clientes = cursor.fetchall()
            clientes.reverse()

        venta_folio_numero = numero_venta_acutual(DB)
        return render_template('/ventas/venta_add.html',
                               title=title,
                               productos=productos,
                               clientes=clientes,
                               fecha=fecha,
                               hora=hora,
                               venta_folio_numero=venta_folio_numero,
                               venta_id = venta_id,
                               funciones_ventas=True,
                               cliente_id=cliente_id,
                               view_redirect=view_redirect,
                               style=style, nav_rol=nav_rol)


@ventas_bp.route('detalle')
@login_required
def ventas_detalles_general():
    """ vista ventas """
    sub_menu = info_sub_menu()
    nav_rol = vista_por_rol(current_user.rol)
    DB = current_user.conexion_db
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM venta_detalle')
        ventas_detalle_general = cursor.fetchall()
    ventas_detalle_general.reverse()
    title_dt = "DETALLE DE VENTAS | GENERAL"
    return render_template('/ventas/ventas_detalle_general.html',
                           title=title_dt,
                           ventas=ventas_detalle_general,
                           nav_rol=nav_rol, sub_menu=sub_menu)


@ventas_bp.route('/view/<id_venta>')
@login_required
def ventas_view(id_venta):
    """acá podemos ver el detalle de la venta por su numero de venta"""
    DB = current_user.conexion_db
    nav_rol = vista_por_rol(current_user.rol)
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM ventas WHERE venta_id =?', (id_venta,))
        data = cursor.fetchall()

        # aca se obtienen los datos de la tanla de productos y servicios de la venta
        cursor = conexion.cursor()
        cursor.execute(
            'SELECT * FROM venta_detalle WHERE venta_dt_venta_id =?', (id_venta,))
        venta_dt = cursor.fetchall()

    # codigo para obtener la tabla de abonos y pagos
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT pago_abono.*, forma_de_pago.forma_de_pago_nombre
            FROM pago_abono
            INNER JOIN forma_de_pago ON pago_abono.pago_abono_forma = forma_de_pago.forma_de_pago_id
            WHERE pago_abono.pago_abono_venta_id = ?
        """, (id_venta,))
        pago_y_abonos = cursor.fetchall()

    # codigo para obtener el detalle de la venta - productos
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT venta_detalle.*, productos.producto_nombre, productos.producto_codigo
            FROM venta_detalle
            INNER JOIN productos ON venta_detalle.venta_dt_producto_id = productos.producto_id
            WHERE venta_detalle.venta_dt_venta_id = ?
        """, (id_venta,))
        dt = cursor.fetchall()

    data_producto = buscador_por_key(DB, 'productos', 'producto_id',
                                     venta_dt[0][2])

    data_cliente = buscador_por_key(DB, 'clientes', 'cliente_id', data[0][2])
    tt_cc_pa = {}
    tt_cc_pa['total'] = sumar_si(
        DB, 'venta_detalle', id_venta, 'venta_dt_venta_id', 'venta_dt_total')
    tt_cc_pa['abono'] = sumar_si(
        DB, 'pago_abono', id_venta, 'pago_abono_venta_id', 'pago_abono_monto')
    tt_cc_pa['cxc'] = tt_cc_pa['total'] - tt_cc_pa['abono']

    datos = {}
    datos['title'] = 'Vista Cliente'
    datos['generales'] = data[0]
    datos['venta_dt'] = dt
    datos['cliente'] = data_cliente
    datos['producto'] = data_producto
    datos['pagos_abonos'] = pago_y_abonos
    datos['id_venta'] = id_venta
    datos['tt_cc_pa'] = tt_cc_pa

    # generate_pdf_(datos, f'venta nro {id_venta}')

    return render_template('/ventas/venta_view.html', title='view', data=data[0],
                           venta_dt=dt, cliente=data_cliente, producto=data_producto,
                           pa=pago_y_abonos, id_venta=id_venta, tt_cc_pa=tt_cc_pa, datos=datos, nav_rol=nav_rol)


@ventas_bp.route('/cxc')
@login_required
def ventas_table_cxc():
    """ Vista de ventas """
    nav_rol = vista_por_rol(current_user.rol)
    sub_menu = info_sub_menu()
    DB = current_user.conexion_db
    data_ventas = ventas_generales_ordenada(DB)
    cxc_general = 0
    for ventas in data_ventas:
        cxc_general += ventas[11]
    total_cxc = cxc_general

    ventas = [
        sublista for sublista in data_ventas if sublista[11] > 0]

    title = "VENTAS POR COBRAR"
    return render_template('/ventas/ventas_table.html', title=title,
                           ventas=ventas, total_cxc=total_cxc, nav_rol=nav_rol, sub_menu=sub_menu)


@ventas_bp.route('add/update', methods=['POST'])
def venta_add_update():
    """Recibo los formularios de la view ventas y los almaceno en mi db"""
    DB = current_user.conexion_db
    datos = request.form  # datos recibidos desde el formulario
    fecha_hora_actual = datetime.now()
    fecha = fecha_hora_actual.date()
    hora = fecha_hora_actual.time()
    venta_fecha = fecha.strftime("%d/%m/%Y")
    venta_hora = hora.strftime("%H:%M")
    venta_folio = numero_venta_acutual(DB)
    venta_id = datos['ventaId']#codigo_unico('v')
    venta_cliente_id = datos['venta_cliente_id']
    venta_observacion = datos['ventaObservacion']
    venta_vendedor_id = current_user.id
    
    confirmar = existe_valor_id(DB, 'ventas', 'venta_id', '1234')
    
    if confirmar == False:
        n = 0
        while n < 100:
            # lista_nueva = []
            clave = f'venta_dt_producto_id_{n}'
            if datos.get(clave):
                venta_dt_id = codigo_unico('v_dt')
                venta_dt_producto_id = datos[clave]
                venta_dt_cantidad = datos[f'venta_dt_cantidad_{n}']
                venta_dt_precio = datos[f'venta_dt_precio_{n}']
                venta_dt_total = int(venta_dt_cantidad) * int(venta_dt_precio)
                entregado = True
                # lista_nueva.append(venta_dt_producto_id)
                # lista_nueva.append(venta_dt_cantidad)
                # lista_nueva.append(venta_dt_precio)
                # lista_nueva.append(venta_dt_total)
    
                with sqlite3.connect(DB) as conexion:
                    cursor = conexion.cursor()
                    # ingreso en la db el detalle de la compra
                    cursor.execute("""INSERT INTO venta_detalle (venta_dt_id, venta_dt_venta_id,
                                    venta_dt_fecha, venta_dt_hora,
                                    venta_dt_cliente_id, venta_dt_vendedor_id, 
                                    venta_dt_producto_id,
                                    venta_dt_precio,venta_dt_cantidad, venta_dt_total,
                                    venta_dt_entregado)
                                    VALUES (?, ?, ?, ?, ?, ?,?, ?, ?,?,?)""",
                                   (venta_dt_id, venta_id, venta_fecha, venta_hora,
                                    venta_cliente_id, venta_vendedor_id, venta_dt_producto_id,
                                    venta_dt_precio, venta_dt_cantidad, venta_dt_total,
                                    entregado))
                    conexion.commit()
            n += 1
    
        if datos['pago_abono_forma'] != "" and datos['pago_abono_monto'] != "":
            pago_abono_id = codigo_unico('pa')
            pago_abono_forma = datos['pago_abono_forma']
            pago_abono_monto = datos['pago_abono_monto']
            numero_de_operacion = datos['pago_abono_numero_de_operacion']
            numero_control = numero_de_control(DB, 'pago_abono')
            origen = f'VENTA| nro:{venta_folio}'
            #  se registra el ingreso de efectivo en la tabla movimiento financiero: efectivo
            if pago_abono_forma == 'pa-01':
                registrar_movimiento_efectivo(DB, venta_id , origen, 0, pago_abono_monto,venta_vendedor_id)
            with sqlite3.connect(DB) as conexion:
                cursor = conexion.cursor()
                # ingreso en la db la forma de pago
                cursor.execute("""INSERT INTO pago_abono (pago_abono_id, pago_abono_forma,
                               pago_abono_monto, pago_abono_fecha,
                               pago_abono_hora, pago_abono_numero,
                               pago_abono_numero_de_operacion, pago_abono_vendedor_id, pago_abono_cliente_id,
                               pago_abono_venta_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                               (pago_abono_id, pago_abono_forma, pago_abono_monto,
                                venta_fecha, venta_hora, numero_control, numero_de_operacion,
                                venta_vendedor_id, venta_cliente_id, venta_id))
                conexion.commit()
    
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            # ingreso en la db la informacion de la venta
            cursor.execute("""INSERT INTO ventas (venta_id, venta_fecha, venta_hora,
                            venta_folio, venta_cliente_id, venta_vendedor_id, venta_observaciones)
                            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                           (venta_id, venta_fecha, venta_hora, venta_folio,
                            venta_cliente_id, venta_vendedor_id, venta_observacion))
            conexion.commit()
    
        flash('venta creada correctamente', 'success')
        return jsonify({'mensaje': 'Venta agregada exitosamente!!'})
    elif confirmar == True:
        return redirect(url_for('ventas.venta_add'))
        
    
    
@ventas_bp.route('/view/<id_venta>/delete/superadmin')
@login_required
def ventas_delete(id_venta):
    #AGREGAR VALIDACION DE DIA
    #AGREGAR VALIDACION DE USUARI
    DB = current_user.conexion_db
    usuario_id = current_user.id
    eliminar_por_id(DB, 'venta_detalle', 'venta_dt_venta_id', id_venta, usuario_id)
    eliminar_por_id(DB, 'ventas', 'venta_id', id_venta, usuario_id)
    eliminar_por_id(DB, 'movimientos_efectivo', 'movimiento_efectivo_origen_id', id_venta, usuario_id)
    eliminar_por_id(DB, 'pago_abono', 'pago_abono_venta_id', id_venta, usuario_id)
    flash(f'eliminada con exito {id_venta}', 'success')
    return redirect(url_for('ventas.ventas_table'))
    
    

        

