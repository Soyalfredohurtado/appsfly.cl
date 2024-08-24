"""Rutas para generar los pdf"""
from flask import Blueprint, redirect, url_for, flash
from script.pdf.generador_pdf import generate_pdf_
from script.python.db.consulta_db import buscador_por_key


pdf_bp = Blueprint('pdf', __name__)




@pdf_bp.route('/cierre_venta_diario/<id_>')
def generate_pdf_cierre_diario(id_):
    """genera el pdf del cierre vebnta diario"""
    DB = current_user.conexion_db

    datos = buscador_por_key(DB, 'cierre_diario_ventas',
                             'cierre_diario_id', id_)
    fecha = datos[1]
    fecha = fecha.replace('/', '-')
    nombre_pdf = f'cierre {fecha}'
    nombre_template = 'cierre_diario.html'
    print(fecha)
    generate_pdf_(datos, nombre_template, nombre_pdf)

    flash('Pdf generado exitosamente')
    return redirect(url_for('movimientos_financiero.cierre_diario_table'))
