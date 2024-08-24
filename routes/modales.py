""" acá va el codigo para guardar información obtenida con modales """
import sqlite3
import os

from flask import Blueprint, flash, request, url_for, redirect, render_template

from datetime import datetime

from flask_login import login_required, current_user

from script.funciones import codigo_unico, numero_de_control
from script.python.fechas import hora_actual, fecha_actual
from script.python.db.rutas_db import ruta_imagenes
from script.python.nav import vista_por_rol
from script.python.db.consulta_db import existe_valor_id, contar_por_key
from script.python.db.operaciones_db import sumar_si, sumar_si_conjunto
from script.python.db.movimientos_financieros import registrar_movimiento_efectivo




modales_bp = Blueprint('modales', __name__)
usuarios_permitidos = [0, 1]


fecha = fecha_actual()
hora = hora_actual()


@modales_bp.route('/gastos')
@login_required
def gastos_view():
    """ vista de gasto"""
    DB = current_user.conexion_db
    if int(current_user.rol) in usuarios_permitidos:
        nav_por_rol = vista_por_rol(current_user.rol)
        title = 'Gastos Registrados'
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute("""SELECT gastos.*, usuarios.usuario_nombre
                FROM gastos
                INNER JOIN usuarios ON gastos.gasto_usuario = usuarios.usuario_id""")
            gastos = cursor.fetchall()
            gastos.reverse()
        return render_template('/modales/gastos_table.html', title=title,
                               gastos=gastos, nav_rol=nav_por_rol)

    else:
        flash('no tiene permiso para acceder')
        return redirect(url_for('dashboard.dashboard'))


@modales_bp.route('add_gasto',  methods=['POST'])
@login_required
def regirtar_gasto():
    """ conectado a ajax para registrat los gastos """
    DB = current_user.conexion_db
    usuario_id = current_user.id
    usuario_db = current_user.conexion_db
    motivo = request.form['motivoGasto']
    monto = int(request.form['montoGasto'])
    nro_control = numero_de_control(DB, 'gastos')
    clasificacion = request.form['clasificacionGasto']
    gasto_id = codigo_unico('g')

    if request.files['comprobanteGasto']:
        imagen = request.files['comprobanteGasto']
        ruta_guardado = ruta_imagenes(usuario_db)
        nombre = f'img-{gasto_id}.jpg'
        # Verificar si el directorio existe, si no, crearlo
        if not os.path.exists(ruta_guardado):
            os.makedirs(ruta_guardado)
        imagen.save(os.path.join(ruta_guardado, nombre))
        imagen_ruta = f'../{ruta_guardado}/{nombre}'
    else:
        imagen_ruta = None
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""INSERT INTO gastos(gasto_id, gasto_fecha, gasto_hora,
                       gasto_monto, gasto_motivo, gasto_usuario, gasto_clasificacion,
                       gasto_nro, gasto_comprobante)
                       VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (gasto_id, fecha, hora, monto, motivo, usuario_id,
                        clasificacion, nro_control, imagen_ruta))
        conexion.commit()
    flash('gasto registrado con existo')
    return redirect(url_for('dashboard.dashboard'))


@modales_bp.route('add_pa',  methods=['POST'])
@login_required
def regirtar_pago_abono():
    """Registra pagos y abonos de la view ventas"""
    DB = current_user.conexion_db
    pa_id = codigo_unico('pa')
    usuario_id = current_user.id
    forma_de_pago = request.form['paFormaDePago']
    monto = int(request.form['paMonto'])
    numero_operacion = request.form['paNumeroOperacion']
    venta_id = request.form['ventaID']
    nro_control = numero_de_control(DB, 'pago_abono')
    cliente_id = request.form['clienteID']
    venta_folio_nro = request.form['numeroVenta']
    origen = f'VENTA nro:{venta_folio_nro} (abono)'
    # se registra el ingreso de efectivo en la tabla movimiento financiero: efectivo
    if forma_de_pago == 'pa-01':
        registrar_movimiento_efectivo(DB, venta_id , origen, 0, monto, usuario_id)

    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""INSERT INTO pago_abono(pago_abono_id, pago_abono_forma, pago_abono_monto, pago_abono_numero,
                       pago_abono_venta_id, pago_abono_cliente_id, pago_abono_vendedor_id, pago_abono_fecha, pago_abono_hora,
                       pago_abono_numero_de_operacion  )
                       VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ? )""", (pa_id, forma_de_pago, monto, nro_control,  venta_id,
                                                                  cliente_id, usuario_id,  fecha, hora, numero_operacion))
        conexion.commit()
    flash('registrado con existo', 'success')
    return redirect(url_for('ventas.ventas_view',  id_venta=venta_id))


@modales_bp.route('/cierre_caja', methods=['POST', 'GET'])
@login_required
def cierre_caja():
    DB = current_user.conexion_db
    if request.method == 'POST':
        # agregar en la db el cierre de la ventas diarias
        fecha_hora_actual = datetime.now()
        fecha_actual = fecha_hora_actual.date()
        cierre_diario_id = codigo_unico('cd')
        usuario_id = current_user.id
        ventas = request.form['cierreCajaVentas']
        ventas_numero = request.form['cierreCajaNumeroVentas']
        ingresos = request.form['cierreCajaIngresos']
        efectivo = request.form['cierreCajaEfectivo']
        transferecia = request.form['cierreCajaTransferencia']
        punto_venta = request.form['cierreCajaPuntoVenta']
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """INSERT INTO cierre_diario_ventas(cierre_diario_id, cierre_diario_vendedor,
                cierre_diario_fecha, cierre_diario_ventas, cierre_diario_ingresos,
                cierre_diario_efectivo, cierre_diario_transferencia,
                cierre_diario_punto_venta, cierre_diaro_ventas_numero)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""", (cierre_diario_id, usuario_id, fecha_actual,
                                                       ventas, ingresos, efectivo, transferecia,
                                                       punto_venta, ventas_numero))
            conexion.commit()
        flash('Cierre de caja exitoso', 'success' )
        return redirect(url_for('dashboard.dashboard'))
    else:
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                f"DELETE FROM cierre_diario_ventas WHERE cierre_diario_fecha= '{fecha}'")
            conexion.commit()
        flash('se aperturo con exito la caja', 'success')
        return redirect(url_for('dashboard.dashboard'))
        

@modales_bp.route('/cierre_caja/fecha', methods=['POST'])
@login_required
def cierre_caja_fecha():
    DB = current_user.conexion_db
    cierre_diario_id = codigo_unico('cd')
    usuario_id = current_user.id
    cierre_fecha_ = datetime.strptime(request.form['cierreCajaFecha2'], '%Y-%m-%d')
    fecha = cierre_fecha_.strftime('%d/%m/%Y') # formateado
    if existe_valor_id(DB, 'cierre_diario_ventas', 'cierre_diario_fecha', fecha):
        flash(f'cierre diaria con fecha: {fecha} existe', 'danger') 

    else:
        ventas = sumar_si(DB, 'venta_detalle', fecha,'venta_dt_fecha', 'venta_dt_total')
        ventas_numero = contar_por_key(DB, 'ventas', 'venta_fecha', fecha)
        ingresos =  sumar_si(DB, 'pago_abono', fecha,'pago_abono_fecha', 'pago_abono_monto')
        efectivo = sumar_si_conjunto(DB, 'pago_abono', 'pago_abono_monto', [['pago_abono_fecha', fecha], ['pago_abono_forma', 'pa-01']])
        transferencia = sumar_si_conjunto(DB, 'pago_abono', 'pago_abono_monto', [['pago_abono_fecha', fecha], ['pago_abono_forma', 'pa-03']])
        punto_venta = sumar_si_conjunto(DB, 'pago_abono', 'pago_abono_monto', [['pago_abono_fecha', fecha], ['pago_abono_forma', 'pa-02']])
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute("""INSERT INTO cierre_diario_ventas(cierre_diario_id, cierre_diario_vendedor,
                cierre_diario_fecha, cierre_diario_ventas, cierre_diario_ingresos,
                cierre_diario_efectivo, cierre_diario_transferencia,
                cierre_diario_punto_venta, cierre_diaro_ventas_numero)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""", (cierre_diario_id, usuario_id, fecha,
                                                       ventas, ingresos, efectivo, transferencia,
                                                       punto_venta, ventas_numero))
            conexion.commit()
        flash(f'agregado cierre dia: Fecha:{fecha}', 'success')
    return redirect(url_for('movimientos_financiero.cierre_diario_table'))
