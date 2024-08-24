"""Codígo para los gastos"""
import sqlite3
import os

from datetime import datetime

from flask import Blueprint, flash, request, url_for, redirect, render_template
from flask_login import login_required, current_user

from script.funciones import codigo_unico
from script.python.db.movimientos_financieros import registrar_movimiento_efectivo
from script.funciones import numero_de_control
from script.python.rutas import validacion_vista_por_rol
from script.python.nav import vista_por_rol, lista_roles
from script.python.db.rutas_db import ruta_imagenes
from script.python.db.consulta_db import datos_tabla_todos, buscador_por_key
from static.style_python.style import style
from script.python.db.delete_db import eliminar_por_id

gastos_bp = Blueprint('gastos', __name__)


usuarios_permitidos = lista_roles(0, 1)


# ----------------------------------- TABLE: Gastos -----------------------------------
@gastos_bp.route('')
@login_required
def gastos_table():
    """ vista de gasto"""
    nav_rol = vista_por_rol(current_user.rol)
    DB = current_user.conexion_db
    title = 'Gastos Registrados'
    gasto_fecha_actual = datetime.now().strftime('%Y-%m-%d')
    gasto_id_ = codigo_unico('g')
    
    #gastos = datos_tabla_todos(DB, 'gastos')
    gastos_categoria = datos_tabla_todos(DB, 'gastos_categoria')
    gastos_por_categoria_suma = []
    
    for gasto in gastos_categoria:
        gasto = gasto + ('0',) 
        gastos_por_categoria_suma.append(gasto) 
    
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""SELECT gastos.*, gastos_categoria.gasto_categoria_nombre 
            FROM gastos
            INNER JOIN gastos_categoria ON gastos.gasto_categoria = gasto_categoria_id""")
        gastos = cursor.fetchall()
    gastos.reverse()

    lista_gastos= []
    
    for gasto in gastos:
            
            db_negocios_usuarios ='./database/relacion_usuarios_negocios.db'
            vendedor = buscador_por_key(db_negocios_usuarios, 'usuarios', 'usuario_id', gasto[6])
            nombre_vendedor = vendedor[3]
            gastosss = list(gasto)
            gastosss.append(nombre_vendedor)
            lista_gastos.append(gastosss)

    return render_template('/gastos/gastos_table.html',
                            title=title,
                            gastos=lista_gastos,
                            nav_rol=nav_rol,
                            fecha_actual=gasto_fecha_actual,
                            gasto_id=gasto_id_,
                            style=style,
                            gastos_categoria=gastos_categoria,
                            gastos_por_categoria=gastos_por_categoria_suma)


# ----------------------------------- ADD: Gastos -------------------------------------
@gastos_bp.route('add_gasto',  methods=['POST'])
@login_required
def gastos_add():
    """ conectado a ajax para registrat los gastos """
    usuario_id = current_user.id
    DB = current_user.conexion_db
    gasto_id = request.form['gastoID']
    motivo = request.form['gastoMotivo']
    monto = int(request.form['gastoMonto'])
    nro_control = numero_de_control(DB, 'gastos')
    categoria = request.form['gastoCategoria']
    fecha_hora_actual = datetime.now()
    fecha = fecha_hora_actual.date()
    hora = 'pendiente'

    if request.files['comprobanteGasto']:
        imagen = request.files['comprobanteGasto']
        ruta_guardado = ruta_imagenes(DB)
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
                       gasto_monto, gasto_motivo, gasto_usuario, gasto_categoria,
                       gasto_nro, gasto_comprobante)
                       VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (gasto_id, fecha, hora, monto, motivo, usuario_id,
                        categoria, nro_control, imagen_ruta))
        conexion.commit()
    origen = f'GASTO: nro:{nro_control},  {motivo}'
    registrar_movimiento_efectivo(DB, gasto_id,origen, 1, monto, usuario_id)
    flash('gasto registrado con existo', 'success')
    return redirect(url_for('dashboard.dashboard'))


# ----------------------------------- DELETE: Gastos -------------------------------------
@gastos_bp.route('/<string:id_>/delete')
@login_required
def gasto_delete(id_):
    """ explicación  """
    DB = current_user.conexion_db
    usuario_id = current_user.id
    if current_user.rol == 0:
        eliminar_por_id(DB, 'movimientos_efectivo', 'movimiento_efectivo_origen_id', id_, usuario_id)
        eliminar_por_id(DB, 'gastos', 'gasto_id', id_, usuario_id)
        flash('Gasto eliminado con exito', 'success')
        return redirect(url_for('gastos.gastos_table'))
    else:
        flash('no tiene premiso para eliminar Gastos', 'danger')
        return redirect(url_for('gastos.gastos_table'))
        


# ----------------------------------- TABLE: Gastos Categoria --------------------------
@gastos_bp.route('/categorias')
@login_required
def gastos_categoria_table():
    """ vista de gasto"""
    usuario_db = current_user.conexion_db
    nav_rol = vista_por_rol(current_user.rol)
    title = 'Gastos - Categorías'
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    gasto_categoria_id = codigo_unico('gc')
    with sqlite3.connect(usuario_db) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""SELECT * FROM gastos_categoria""")
        claisicacion_gastos = cursor.fetchall()
    return render_template('/gastos/gastos_categoria_table.html', title=title,
                           claisicacion_gastos=claisicacion_gastos, nav_rol=nav_rol,
                           fecha_actual=fecha_actual, gasto_categoria_id=gasto_categoria_id,
                           style=style)


# ----------------------------------- ADD: Gastos Categoría  --------------------------
@gastos_bp.route('/categoria/add',  methods=['POST'])
@login_required
def gastos_categoria_add():
    """Se agrega una nueva categoria """
    usuario_id = current_user.id
    DB = current_user.conexion_db
    categoria_id = request.form['categoriaGastoID']
    categoria_nombre = request.form['categoriaGastoNombre']
    categoria_status = request.form['categoriaGastoStatus']
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""INSERT INTO gastos_categoria(gasto_categoria_id,
                       gasto_categoria_nombre,
                       gasto_categoria_status, gasto_categoria_usuario_id )
                       VALUES(?, ?, ?, ?)""",
                       (categoria_id, categoria_nombre,
                        categoria_status, usuario_id))
        conexion.commit()
    flash('Nueva categoria registrada con exito', 'success')
    return redirect(url_for('gastos.gastos_categoria_table'))


@gastos_bp.route('/view/<string:id_>')
@login_required
def gasto_view(id_):
    """Codígo para editar los gastos """
    DB = current_user.conexion_db    
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM gastos WHERE gasto_id =?', (id_,))
        gasto = cursor.fetchall()
        data = {
            'title':'Detalle Gasto',
            'gasto': gasto
        }
    return render_template('/gastos/gasto_view.html', data=data)



@gastos_bp.route('/edit/<string:id_>')
@login_required
def gasto_edit(id_):
    """Codígo para editar los gastos """
    DB = current_user.conexion_db    
    with sqlite3.connect(DB) as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM gastos WHERE gasto_id =?', (id_,))
        gasto = cursor.fetchall()
        data = {
            'title':'Detalle Gasto',
            'gasto': gasto
        }
    return render_template('/gastos/gastos_edit.html', data=data)
       
        

