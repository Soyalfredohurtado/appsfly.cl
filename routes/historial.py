"""Acá van las rutas relacionadas con los clientes"""

import sqlite3

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from static.style_python.style import style


historial_bp = Blueprint('historial', __name__)

historial_bp.route('db')
@login_required
def historial_table():
    DB = current_user.conexion_db
    return redirect(url_for('login'))