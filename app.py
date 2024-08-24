"""  este es el codigo inicial   """
from datetime import datetime
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from routes import ventas_bp, productos_bp, clientes_bp, dashboard_bp
from routes import usuarios_bp, movimientos_financiero_bp, modales_bp
from routes import pdf_bp, gastos_bp, historial_bp
from models.entities.User import User
from models.ModelUser import ModelUser


app = Flask(__name__)
app.secret_key = 'kjguyfu546543263215646545864213212121211'



app.register_blueprint(ventas_bp, url_prefix='/ventas')
app.register_blueprint(productos_bp, url_prefix='/productos_y_servicios')
app.register_blueprint(clientes_bp, url_prefix='/clientes')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
app.register_blueprint(movimientos_financiero_bp,
                       url_prefix='/movimientos_financiero')
app.register_blueprint(modales_bp, url_prefix='/modales')
app.register_blueprint(pdf_bp, url_prefix='/pdf')
app.register_blueprint(gastos_bp, url_prefix='/gastos')
app.register_blueprint(historial_bp, url_prefix='/historial')

# ====================== LOGIN ===========================
db_ = './database/relacion_usuarios_negocios.db'
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'
login_manager.login_message = 'Inicia sesión para acceder a esta página'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(id_):
    """ descripcion """
    return ModelUser.get_by_id(db_, id_)


@app.route('/',  methods=['GET', 'POST'])
def login():
    """" Ruta incial para el ingreso al sistema """
    datos = {}
    datos['title'] = 'titulo'
    title = 'Iniciar Sesión'
    if request.method == 'POST':
        correo = request.form['usuario_correo']
        usuario_correo = correo.lower()
        user = User(None, usuario_correo, request.form['usuario_password'], None, None, None)
        # logiar al usuario
        logged_user = ModelUser.login(db_, user)
        if logged_user is not None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('contraseña invalida',  'danger')
                return render_template('login.html', datos=datos, usuario_correo=usuario_correo)
        else:
            flash('usuario no existe', 'danger')
            return render_template('login.html', title=title,  usuario_correo=usuario_correo)
    else:
        return render_template('login.html', title=title)


@app.route('/logout')
def logout():
    """Ruta para salir del sistema  """
    logout_user()
    flash('se cerro la session exitosamente', 'success')
    return redirect(url_for('login'))



@app.route('/admin/db')
@login_required
def vista_db():
    db = current_user.conexion_db
    with sqlite3.connect(db) as conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        
    esquema_db = {}
    for tabla in tablas:
        nombre_tabla = tabla[0]
        cursor.execute(f"PRAGMA table_info({nombre_tabla});")
        columnas = cursor.fetchall()
        esquema_db[nombre_tabla] = [columna[1] for columna in columnas] 
    return render_template('/db/db_table.html', esquema_db=esquema_db)
    
@app.template_filter('formatear_fecha')
def formato_fecha_iso_a_dia_mes_ano(fecha_iso):
    try:
        fecha = datetime.strptime(fecha_iso, '%Y-%m-%d')
        return fecha.strftime('%d-%m-%Y')
    except ValueError:
        return fecha_iso  # Devuelve la fecha original si hay un error de formato
        
        
@app.template_filter('mayuscula')
def formato_mayuscula(text):
    try: 
        return text.upper()
    except ValueError:
        return text  # Devuelve la fecha original si hay un error de formato        
        
        

if __name__ == '__main__':
    app.run(port=3000, debug=True)
