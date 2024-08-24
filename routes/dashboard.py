""" aca van las rutas relacionadas con el dashboard"""
from datetime import datetime

from flask_login import login_required, current_user
from flask import Blueprint, render_template, flash, redirect, url_for
from script.funciones import codigo_unico
from script.python.db.operaciones_db import sumar_si, sumar_si_conjunto
from script.python.db.consulta_db import ventas_generales_ordenada, contar_por_key, datos_tabla_todos
from script.python.nav import vista_por_rol, info_sub_menu
from static.style_python.style import style


dashboard_bp = Blueprint('dashboard', __name__)
# ============================= dashboard =================================

@dashboard_bp.route('')
@login_required
def dashboard():
    if current_user.conexion_db:
        """" ejemplo rellenar """
        nav_rol = vista_por_rol(current_user.rol)
        sub_menu = info_sub_menu()
        DB = current_user.conexion_db
        title = 'Dashboard'
        datos = {}
        fecha_hora_actual = datetime.now()
        fecha = fecha_hora_actual.date()
        fecha_ = fecha.strftime("%d/%m/%Y")
        datos['fecha_'] = fecha
        datos['fecha'] = fecha_
        mes_actual = fecha.strftime("%m")
        datos['por_entregar'] = ''
    
        # __________________________  BOX - Caja _________________________________
        caja = {}
        cierre_diario_actual = contar_por_key(DB, 'cierre_diario_ventas',
                                              'cierre_diario_fecha', fecha_)
    
        caja['i_cierre_caja'] = 'hidden' if cierre_diario_actual > 0 else ''
        caja['i_abir_caja'] = 'hidden' if cierre_diario_actual == 0 else ''
        ventas_dia_actual = sumar_si(DB, 'venta_detalle', fecha_,
                                     'venta_dt_fecha', 'venta_dt_total')
        ingresos_dia_actual = sumar_si(DB, 'pago_abono', fecha_,
                                       'pago_abono_fecha', 'pago_abono_monto')
        gastos_dia_actual = sumar_si(DB, 'gastos', fecha_,
                                     'gasto_fecha', 'gasto_monto')
        caja['ventas_numero_dia'] = contar_por_key(
            DB, 'ventas', 'venta_fecha', fecha_)
        caja['ventas_dia'] = ventas_dia_actual
        caja['ingresos_dia'] = ingresos_dia_actual
        caja['gastos_dia'] = gastos_dia_actual
        caja['efectivo_dia'] = sumar_si_conjunto(
            DB, 'pago_abono', 'pago_abono_monto', [
                ['pago_abono_fecha', fecha_], ['pago_abono_forma', 'pa-01']])
        caja['transferencia_dia'] = sumar_si_conjunto(
            DB, 'pago_abono', 'pago_abono_monto', [
                ['pago_abono_fecha', fecha_], ['pago_abono_forma', 'pa-03']])
        caja['punto_venta_dia'] = sumar_si_conjunto(
            DB, 'pago_abono', 'pago_abono_monto', [
                ['pago_abono_fecha', fecha_], ['pago_abono_forma', 'pa-02']])
        datos['caja'] = caja
    
        # __________________________________ BOX - Gastos _____________________________________
        box_gasto_efecivo = {}
        gasto_id_ = codigo_unico('g')
        #mes_actual_iso = fecha_actual.strftime("%m")
        gastos_categoria = datos_tabla_todos(DB, 'gastos_categoria')
        tabla_gastos_todos = datos_tabla_todos(DB, 'gastos')
        total_gasto_mes_= 0
        fecha_mes_ = fecha.month
        for gasto in tabla_gastos_todos:
            fecha_str = gasto[1]
            monto_ = int(gasto[3])
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            fecha_mes = fecha.month
            if fecha_mes == fecha_mes_: #AGREGAR LOGICA PARA COMPARAR CON EL MES
                total_gasto_mes_ += monto_
        
        entrada = sumar_si(DB, 'movimientos_efectivo',0, 'movimiento_efectivo_tipo', 'movimiento_efectivo_monto')
        salida = sumar_si(DB, 'movimientos_efectivo', 1, 'movimiento_efectivo_tipo', 'movimiento_efectivo_monto')
        saldo = entrada - salida
        box_gasto_efecivo['gastos_mes'] = total_gasto_mes_
        box_gasto_efecivo['efectivo_disponible'] = saldo
        datos['box_gasto_efecivo'] = box_gasto_efecivo
    
    
        # __________________________________ BOX - CXC _____________________________________
    
        ventas_generales = ventas_generales_ordenada(DB)
        cxc_general = 0
      
        for ventas in ventas_generales:
            cxc_general += ventas[10]
            pass
        datos['cxc'] = cxc_general
    
        datos['cxc_lista'] = 'pendiente'
    
        # __________________________________ BOX - Ventas Mes  _____________________________________
    
        ventas_mes_actual = 0
        for venta in ventas_generales:
    
            fecha_venta_str = venta[3]
            # Convertir la cadena a objeto de fecha
            fecha_venta = datetime.strptime(fecha_venta_str, "%d/%m/%Y")
            mes_de_la_venta = fecha_venta.strftime("%m")
            if mes_de_la_venta == mes_actual:
                ventas_mes_actual += venta[9]
        datos['total_venta_mes_actual'] = ventas_mes_actual
    
        # _________________________________________ MODALES _______________________________________
    
        return render_template('/dashboard/dashboard.html', title=title,
                                datos=datos, style=style, nav_rol=nav_rol,
                                box_gasto_efecivo=box_gasto_efecivo,
                                gastos_categoria=gastos_categoria,
                                gasto_id=gasto_id_,
                                sub_menu=sub_menu)
    else: 
        title = 'Dashboard'
        nombre = current_user.fullname
        return render_template('/dashboard/dashboard_nuevo_usuario.html', title=title, name=nombre)
