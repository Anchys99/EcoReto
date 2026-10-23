import os
import psycopg
from psycopg.rows import dict_row
from flask import Blueprint, render_template, request, redirect, url_for, flash

main_bp = Blueprint('main', __name__)

def conectar_db():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Falta configurar la variable DATABASE_URL")
    return psycopg.connect(url, row_factory=dict_row)

@main_bp.route('/')
def index():
    try:
        conexion = conectar_db()
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT id, titulo, categoria, descripcion, propuesto_por 
                FROM acciones 
                ORDER BY id DESC
            """)
            acciones = cursor.fetchall()
            
            # Cálculo de métricas básicas
            total_acciones = len(acciones)
            agua_ahorrada = total_acciones * 50
            reciclaje = total_acciones * 3
            co2_evitado = total_acciones * 2
            
            stats = {
                'total': total_acciones,
                'agua': agua_ahorrada,
                'reciclaje': reciclaje,
                'co2': co2_evitado
            }
        conexion.close()
        return render_template('index.html', acciones=acciones, stats=stats)
    except Exception as e:
        return f"Error de conexión o consulta: {e}", 500

@main_bp.route('/nueva', methods=['GET', 'POST'])
def nueva_accion():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        categoria = request.form.get('categoria')
        descripcion = request.form.get('descripcion')
        propuesto_por = request.form.get('propuesto_por', 'Estudiante')

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

    return render_template('formulario.html', accion=None)

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
                    SET titulo=%s, categoria=%s, descripcion=%s, propuesto_por=%s 
                    WHERE id=%s
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