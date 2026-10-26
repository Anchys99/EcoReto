from flask import Blueprint, render_template, request, redirect, url_for, session
import psycopg
import psycopg.rows
import os

main_bp = Blueprint('main', __name__)

def conectar_db():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Falta configurar la variable DATABASE_URL")
    return psycopg.connect(url, sslmode='require', row_factory=psycopg.rows.dict_row)

@main_bp.route('/')
def index():
    if 'usuario' not in session:
        return redirect(url_for('main.login'))
    
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT id, titulo, categoria, descripcion, propuesto_por 
                FROM acciones 
                ORDER BY id DESC
            """)
            acciones = cursor.fetchall()
            
            total_acciones = len(acciones)
            agua_ahorrada = total_acciones * 50
            reciclaje = total_acciones * 5
            co2_evitado = total_acciones * 45
            
            stats = {
                'total': total_acciones,
                'agua': agua_ahorrada,
                'reciclaje': reciclaje,
                'co2': co2_evitado
            }
    finally:
        conexion.close()
        
    return render_template('index.html', acciones=acciones, stats=stats)

@main_bp.route('/nueva', methods=['GET', 'POST'])
def nueva_accion():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        categoria = request.form.get('categoria')
        descripcion = request.form.get('descripcion')
        propuesto_por = request.form.get('propuesto_por')
        
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO acciones (titulo, categoria, descripcion, propuesto_por)
                    VALUES (%s, %s, %s, %s)
                """, (titulo, categoria, descripcion, propuesto_por))
                conexion.commit()
        finally:
            conexion.close()
            
        return redirect(url_for('main.index'))
        
    return render_template('formulario.html')

@main_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_accion(id):
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            if request.method == 'POST':
                titulo = request.form.get('titulo')
                categoria = request.form.get('categoria')
                descripcion = request.form.get('descripcion')
                propuesto_por = request.form.get('propuesto_por')
                
                cursor.execute("""
                    UPDATE acciones 
                    SET titulo = %s, categoria = %s, descripcion = %s, propuesto_por = %s 
                    WHERE id = %s
                """, (titulo, categoria, descripcion, propuesto_por, id))
                conexion.commit()
                return redirect(url_for('main.index'))
            
            cursor.execute("SELECT * FROM acciones WHERE id = %s", (id,))
            accion = cursor.fetchone()
    finally:
        conexion.close()
        
    return render_template('formulario.html', accion=accion)

@main_bp.route('/detalles/<int:id>')
def detalles_accion(id):
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM acciones WHERE id = %s", (id,))
            accion = cursor.fetchone()
    finally:
        conexion.close()
        
    return render_template('detalles.html', accion=accion)

@main_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_accion(id):
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM acciones WHERE id = %s", (id,))
            conexion.commit()
    finally:
        conexion.close()
        
    return redirect(url_for('main.index'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM usuarios WHERE username = %s AND password = %s",
                    (username, password)
                )
                user = cursor.fetchone()
                if user:
                    session['usuario'] = user['username']
                    return redirect(url_for('main.index'))
        finally:
            conexion.close()
        # Si falla el login
        return render_template('login.html', error="Usuario o contraseña incorrectos")
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('main.login'))

@main_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conexion = conectar_db()
        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (username, password) VALUES (%s, %s)",
                    (username, password)
                )
                conexion.commit()
        finally:
            conexion.close()
            
        return redirect(url_for('main.login'))
        
    return render_template('registro.html')