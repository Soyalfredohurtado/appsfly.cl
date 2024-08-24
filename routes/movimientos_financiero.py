""" aca van las rutas relacionadas con el dashboard"""
import sqlite3

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from script.python.db.consulta_db import datos_tabla_todos
from script.python.nav import vista_por_rol
from script.python.db.consulta_db import ventas_generales_ordenada, datos_tabla_, datos_tabla_todos
from script.python.db.operaciones_db import sumar_si
from static.style_python.style import style
from script.python.db.movimientos_financieros import registrar_movimiento_efectivo
from script.funciones import codigo_unico

movimientos_financiero_bp = Blueprint('movimientos_financiero', __name__)

usuarios_permitidos = [0, 1]


# ============================= dashboard =================================

@login_required
@movimientos_financiero_bp.route('/')
def pagos_abonos_table():
    """aca va la tabla de los movimientos financieros un das"""
    DB = current_user.conexion_db
    if int(current_user.rol) in usuarios_permitidos:
        nav_por_rol = vista_por_rol(current_user.rol)
        title = 'Pagos y Abonos'
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
            pagos_abonos.reverse()
            conexion.commit()
        return render_template('/movimientos_financieros/pagos_abonos_table.html',
                               title=title, pagos_abonos=pagos_abonos, nav_rol=nav_por_rol)


@movimientos_financiero_bp.route('cierre_ventas_diario')
@login_required
def cierre_diario_table():
    """se crea la tabla de cierre"""
    DB = current_user.conexion_db
    nav_rol = vista_por_rol(current_user.rol)
    data = {}
    data['title'] = 'Cierre Ventas Diario'
    cierres = datos_tabla_todos(DB, 'cierre_diario_ventas')
    cierres_ordenados = []
    for cierre in cierres:
        cierres_ordenados.insert(0, cierre)
    data['cierres'] = cierres_ordenados
    style = {'m_div': 'input-group mb-2',
         'm_span': 'input-group-text w-25',
         'm_input': 'form-control text-center mil_000',
         'btn': 'btn btn-success btn-sm mt-0 mb-0 w-25',
         'link': 'btn btn-sm w-100 btn-primary m-2'
         }
    return render_template('/movimientos_financieros/cierre_ventas_diario.html', nav_rol=nav_rol, data=data, style=style)


@movimientos_financiero_bp.route('cierre_ventas_diario/view/<string:id_>')
@login_required
def cierre_diario_view(id_):
    """retorna la vista del cierre diario """
    DB = current_user.conexion_db
    nav_rol = vista_por_rol(current_user.rol)
    data_ventas = ventas_generales_ordenada(DB)
    ventas = []
     
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM cierre_diario_ventas WHERE cierre_diario_id =?', (id_,))
        data = cursor.fetchone()
    for venta in data_ventas:
        if venta[3] == data[1]:
            ventas.append(venta)
    title = f'Cierre Diarío'

    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute('''SELECT pago_abono.*, usuarios.usuario_nombre, clientes.cliente_nombre, ventas.venta_folio, forma_de_pago.forma_de_pago_nombre
                            FROM pago_abono
                            INNER JOIN usuarios ON pago_abono.pago_abono_vendedor_id = usuarios.usuario_id
                            INNER JOIN clientes ON pago_abono.pago_abono_cliente_id = clientes.cliente_id
                            INNER JOIN ventas ON pago_abono.pago_abono_venta_id = ventas.venta_id
                            INNER JOIN forma_de_pago ON pago_abono.pago_abono_forma = forma_de_pago.forma_de_pago_id'''
                           )
        pagos_abonos__ = cursor.fetchall()
        pagos_abonos__.reverse()
        conexion.commit()
    pagos_abonos = []
    for pago in pagos_abonos__:
        if pago[7] == data[1]:
            pagos_abonos.append(pago)

    return render_template('/movimientos_financieros/cierre_ventas_diario_view.html',
                            data = data, title=title, ventas=ventas,
                            nav_rol=nav_rol, pagos_abonos=pagos_abonos)
                            

@movimientos_financiero_bp.route('/efectivo')
@login_required
def movimiento_financiero_efectivo():
    """aca va la tabla de los movimientos del efectivo"""
    DB = current_user.conexion_db
    ajuste_id = codigo_unico('me')
    title = 'Movimientos: Efectivo'
    movimientos_efectivo = datos_tabla_todos(DB, 'movimientos_efectivo')
    movimientos_efectivo.reverse()
    entrada = sumar_si(DB, 'movimientos_efectivo',0,
                   'movimiento_efectivo_tipo', 'movimiento_efectivo_monto')
    salida = sumar_si(DB, 'movimientos_efectivo', 1,
                  'movimiento_efectivo_tipo', 'movimiento_efectivo_monto')
    saldo = entrada - salida
    

    return render_template('/movimientos_financieros/movimiento_efectivo_table.html',
                           title=title, movimientos_efectivo=movimientos_efectivo,
                           saldo=saldo, entrada=entrada, salida=salida, style=style,
                           ajuste_id = ajuste_id)
       
                           
@movimientos_financiero_bp.route('/efectivo/ajuste',  methods=['POST'])
@login_required
def movimiento_financiero_efectivo_ajuste(): 
    rol = current_user.rol
    if rol == '0':
        ajuste_id = request.form['movimientoEfectivoAjusteID']
        tipo = request.form['movimientoEfectivoAjusteTipo']
        motivo = request.form['movimientoEfectivoAjusteMotivo']
        origen = f'AJUSTE: {motivo}'
        monto = request.form['movimientoEfectivoAjusteMonto']
        usuario_id = current_user.id
        registrar_movimiento_efectivo(DB, ajuste_id, origen, tipo, monto, usuario_id)
        flash(f'registrado con exito', 'success')
        return redirect(url_for('movimientos_financiero.movimiento_financiero_efectivo'))
    else:
        flash(f'No esta autorizado para hacer ajustes de efectivo', 'danger')
        return redirect(url_for('movimientos_financiero.movimiento_financiero_efectivo'))
    