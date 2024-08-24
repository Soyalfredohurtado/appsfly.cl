"""" descripcion """
import sqlite3
from datetime import datetime
import os

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from script.funciones import codigo_unico
from script.python.rutas import validacion_vista_por_rol
from script.python.nav import vista_por_rol, lista_roles, info_sub_menu
from script.python.db.consulta_db import buscador_por_key, existe_valor_id
from script.python.db.crud.db_create import create_usuario
from script.python.db.crud.db_delete import *
from static.style_python.style import style
from database.script.negocio_nueva_db import creacion_db_negocio
from script.python.validacion_rut import validar_rut, formatear_rut

usuarios_bp = Blueprint('usuarios', __name__)
usuarios_permitidos = lista_roles(0, 1, 11)

datos = {}

# ----------------------------- usuarios: TABLE --------------------------------
@usuarios_bp.route('')
@login_required
def usuarios_table():
    """descripción"""
    DB = current_user.conexion_db
    nav_rol = vista_por_rol(current_user.rol)
    datos['title'] = 'USUARIOS'
    validacion_vista_rol = validacion_vista_por_rol(current_user.rol, [0, 11])
    if validacion_vista_rol == True:
        sub_menu = info_sub_menu()
        with sqlite3.connect(DB) as conexion:
            cursor = conexion.cursor()
            cursor.execute('SELECT * FROM usuarios')
            usuarios = cursor.fetchall()
            datos['usuarios'] = usuarios
        return render_template('/usuarios/usuarios_table.html', datos=datos, nav_rol=nav_rol, sub_menu =sub_menu )
    else:
        return redirect(url_for('dashboard.dashboard'))

# ----------------------------- usuarios: ADD --------------------------------
@usuarios_bp.route('registar-usuario', methods=['POST', 'GET'])  
def create_usuario():
    """ descripcion
    status usuarios:
    0: no activado
    1: activo
    11: activo super-admin (creador de negocio)
    2: desactivado
    3: eliminado
    9: restringido"""
    DB = './database/relacion_usuarios_negocios.db'
    if request.method == 'POST':        
        password = request.form['usuarioPasswordNueva']
        password_confirmada = request.form['usuarioPasswordNuevaConfirmada']
        usuario_id = request.form['usuarioNuevoID']
        documento_tipo = request.form['usuarioTipoDocumento']
        documento_numero = request.form['usuarioNumeroDocumento']
        nombre_apellido = request.form['usuarioNuevoNombre']
        usuario_nombre = nombre_apellido.lower()
        correo = request.form['usuarioNuevoCorreo']
        usuario_correo = correo.lower()
        numero_area = request.form['usuarioNuevoNumeroArea']
        numero_contacto = request.form['usuarioNuevoNumeroContacto']
        usuario_status = 1
        password_haseada = generate_password_hash(password)
        rut_correcto = validar_rut(documento_numero)
        error_documento = ''
        
        if documento_tipo == '0':
            documento_numero = formatear_rut(documento_numero)
        
        existe_rut = existe_valor_id(DB , 'usuarios', 'usuario_numero_documento',documento_numero)
        e_mail = existe_valor_id(DB , 'usuarios', 'usuario_correo',usuario_correo )

        if existe_rut or e_mail:
            error__ = 'Correo Electrónico'
            if existe_rut:
                error__ = 'RUT'
            flash(f'el {error__} ingresado se encuentra registrado', 'warning')
            return redirect(url_for('login', documento_numero=documento_numero, nombre_apellido=nombre_apellido, numero_contacto=numero_contacto, error_documento=error_documento))

        else:
            if documento_tipo == '0' and rut_correcto == False:
                error_documento = 'text-danger'
                flash(f'rut ingresado no valido {error_documento}')
                return redirect(url_for('usuarios.create_usuario', documento_numero=documento_numero, nombre_apellido=nombre_apellido, numero_contacto=numero_contacto, error_documento=error_documento))
            else:
                if password_confirmada == password:
                    with sqlite3.connect('./database/relacion_usuarios_negocios.db') as conexion:
                        cursor = conexion.cursor()
                        cursor.execute('''INSERT INTO usuarios (usuario_id, usuario_tipo_documento,
                        usuario_numero_documento, usuario_nombre, usuario_status, usuario_password,
                        usuario_correo, usuario_telefono_area, usuario_telefono_numero )VALUES(?,?,?,?,?,?,?,?,?)''',
                        (usuario_id, documento_tipo, documento_numero, usuario_nombre, usuario_status,
                        password_haseada, usuario_correo, numero_area, numero_contacto))
                        conexion.commit()
                    flash(f'usuario creado con exito', 'success')
                    return redirect(url_for('login'))
                else: 
                    flash('contraseña no coincide', 'danger')
                return redirect(url_for('usuarios.create_usuario', documento_numero=documento_numero, nombre_apellido=nombre_apellido, numero_contacto=numero_contacto))
    else:
        datos['title'] = 'Registro Nuevo Usuario'
        datos['usuario_id'] = codigo_unico('u')
        return render_template('/usuarios/usuarios_add.html', datos=datos, style=style)

    
# ----------------------------- usuarios: PERFIL -------------------------------
@usuarios_bp.route('perfil') 
@login_required
def usuario_perfil():
    if current_user.rol != '':
        nav_rol = vista_por_rol(current_user.rol)
    else:
        nav_rol = ''
        
    datos['title'] = 'Registro Nuevo Usuario'
    datos_usuarios = buscador_por_key('./database/relacion_usuarios_negocios.db', 'usuarios', 'usuario_id', current_user.id)
    return render_template('/usuarios/usuario_perfil.html',
    datos=datos, datos_usuarios=datos_usuarios, style=style, nav_rol=nav_rol)

@usuarios_bp.route('/perfil/cambiar_password', methods=['GET', 'POST'])
@login_required
def usuario_cambiar_password():
    """ """
    if request.method == 'POST':
        usuario_id = request.form['usuarioID']
        password_actual = request.form['usuarioPasswordActual']
        password_nuevo = request.form['usuarioPasswordNueva']
        password_nuevo_confirmado = request.form['usuarioPasswordNuevaConfirmada']
        pasword_hasd = generate_password_hash(password_nuevo)
        usuario_status = 1
        hashed_password = '31465465461321aasdasasasasas' #taer la contrase�0�9a desde la base dato
        #password_correcta =  check_password_hash(hashed_password, password_actual)
        if password_nuevo == password_nuevo_confirmado:
            # HASHEAR Y ACTUALIZAR LA CONTRASE�0�5A
            with sqlite3.connect('./database/relacion_usuarios_negocios.db') as conexion:
                cursor = conexion.cursor()
                cursor.execute("""UPDATE usuarios
                                SET usuario_password = ?
                                WHERE usuario_id = ?""",
                                (pasword_hasd, usuario_id))
                conexion.commit()
            flash(f'contraseña actualizada con exito', 'success')
            return redirect(url_for('usuarios.usuario_perfil'))
        else:
            flash('contraseña erronea', 'danger')
            return redirect(url_for('usuarios.usuario_perfil'))
    else: 
        flash('no autorizado para cambiar contraseña', 'danger')
        return redirect(url_for('usuarios.usuario_perfil'))
        
        
#---------------------------------- NEGOCIOS ---------------------------------------

@usuarios_bp.route('/negocios', methods=['GET', 'POST'])
@login_required
def negocios():
    """ 
    
    ------   status negocios  --------
    0: 
    1: activo
    11: suspendio - no pago 
    21: elininada
        
    """
    DB_negocio_usuario = './database/relacion_usuarios_negocios.db'
    DB = current_user.conexion_db
    if current_user.rol:
        nav_rol = vista_por_rol(current_user.rol)
    else:
        nav_rol = ''
    datos['title'] = 'Negocios'
    if request.method == 'POST':
        #### VALIDAR QUE EL CORREO NO ESTE REPETIDO USUARIO Y NEGOCIO
        usuario_id = request.form['negocioNuevoUsuarioID']
        negocio_id = request.form['negocioNuevoID']
        tipo_negocio = request.form['negocioNuevoTipo']
        email_form =  request.form['negocioNuevoCorreo']
        correo = email_form.lower()  # email formateado
        nombre = request.form['negocioNuevoNombre']
        documento_tipo = request.form['negocioTipoDocumento']
        documento_numero = request.form['negocioNumeroDocumento']
        direccion = request.form['negocioNuevoDireccion']
        direccion = direccion.lower()
        telefono_area = request.form['negocioTelefonoArea']
        telefono_numero = request.form['negocioTelefonoNumero']
        negocio_status = 1
        usuario_rol = 11
        usuario_status = 1 
        numero_de_control  = 1#
        documento_numero1 = documento_numero.lower()
        documento_numero2 = documento_numero1.replace(' ','')
        fecha_actual = datetime.now()
        fecha = fecha_actual.date().isoformat()
        nombre_db = f'{numero_de_control}_{documento_numero2}.sql'
        ruta = './database/negocios/'
        ruta_y_nombre = os.path.join(ruta,nombre_db)
        rut_valido = validar_rut(documento_numero)
        if documento_tipo == '0':
            documento_numero = formatear_rut(documento_numero)
        existe_rut = existe_valor_id(DB_negocio_usuario , 'negocios', 'negocio_documento_numero',documento_numero)        

        #se valida que el rut ingresado sea valido
        print(existe_rut, type(documento_tipo), documento_tipo)
        if rut_valido == False:
            negocio_id = codigo_unico('ne')
            flash('rut ingresado no es valido o no existe', 'warning')
            return render_template('/negocios/negocio_add.html', style=style, datos=datos, nav_rol=nav_rol, negocio_id = negocio_id)
        elif existe_rut == True and documento_tipo =='0':
            negocio_id = codigo_unico('ne')
            flash('No se pudo completar el registro. El RUT ingresado ya está registrado en nuestro sistema.', 'warning')
            return render_template('/negocios/negocio_add.html', style=style, datos=datos, nav_rol=nav_rol, negocio_id = negocio_id)
        else:
            with sqlite3.connect('./database/relacion_usuarios_negocios.db') as conexion:
                cursor = conexion.cursor()
                # se crear el perfil de negocio en la dn negocio
                cursor.execute('''INSERT INTO negocios (negocio_id, negocio_tipo,
                                negocio_nombre, negocio_correo, negocio_documento_tipo, negocio_documento_numero,
                                negocio_direccion, negocio_telefono_area, negocio_telefono_numero, negocio_status, negocio_conexion_db)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (negocio_id, tipo_negocio, nombre, correo, documento_tipo, documento_numero2,
                                direccion, telefono_area, telefono_numero, negocio_status, ruta_y_nombre))
                # se asocia el usuario al negocio en la db relacion_usiario_negocio con el rol 11
                cursor.execute('''INSERT INTO relacion_usuario_negocio (usuario_id, negocio_id, usuario_rol, usuario_status, db_asignada, fecha_asignacion)
                                VALUES (?,?,?,?,?,?)''',(usuario_id, negocio_id, usuario_rol,usuario_status, ruta_y_nombre, fecha ))
        
            creacion_db_negocio(ruta_y_nombre)
            return  render_template('/negocios/bienvenida_negocio_nuevo.html', negocio_nombre = nombre)
    else:
        negocio_id = codigo_unico('ne')
        return render_template('/negocios/negocio_add.html', style=style, datos=datos, nav_rol=nav_rol, negocio_id = negocio_id)
        
@usuarios_bp.route('/negocios/table')
@login_required
def negocios_table():
    """
    descripción
    """
    negocios_table = 0
    with sqlite3.connect('./database/relacion_usuarios_negocios.db') as conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT * FROM negocios')
        negocios_table = cursor.fetchall()
        cursor.execute('SELECT * FROM relacion_usuario_negocio')
        relacion_usuario_negocio = cursor.fetchall()
        cursor.execute('SELECT * FROM usuarios')
        usuarios_table = cursor.fetchall()
    return render_template('/negocios/negocios_table.html', negocios_table=negocios_table, relacion_usuario_negocio=relacion_usuario_negocio, usuarios_table=usuarios_table)

    
    
    
    
    
    