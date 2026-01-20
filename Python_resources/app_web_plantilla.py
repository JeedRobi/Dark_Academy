from flask import Flask, render_template, request, redirect, url_for
from conectar_logger import connect_to_mysql
from config import config # Aquí debes poner tu configuración de acceso a la BDA
from DA_plantilla_alumnos import use_database
import os

# para la seguridad básica
from flask import session, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Ruta absoluta a los templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)
app.secret_key = "Me_Gusta_Python" # Necesario para sesiones

DB_NAME = config.get('database') # Aquí pon tu BDA

############################################
#          SEGURIDAD (Avanzado)          #
############################################

# Decorador para proteger rutas
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login")) # redirige a login.html
        return f(*args, **kwargs) # método asociado a una ruta
    return wrapper


# Ruta de login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        # Conectar a la BDA y verificar credenciales
        conn = connect_to_mysql(config)
        if conn is None:
            flash("No se pudo conectar a la BDA")
            return render_template("login2.html")
        
        cursor = conn.cursor()
        use_database(conn, cursor, DB_NAME)

        sql = "SELECT password FROM usuarios WHERE usuario = %s"
        cursor.execute(sql, (usuario,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()

        if resultado and check_password_hash(resultado[0], password):
            session["usuario"] = usuario
            return redirect(url_for("inicio"))
        else:
            flash("Usuario o contraseña incorrectos")

    return render_template("login2.html")


# Ruta página principal
@app.route("/inicio")
@login_required
def inicio():
    return render_template("inicio.html", usuario=session["usuario"])

# Ruta para cerrar sesión
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Ruta de registro
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        # Validar que los campos no estén vacíos
        if not usuario or not password:
            flash("Usuario y contraseña son requeridos")
            return render_template("registro.html")

        # Conectar a la BDA
        conn = connect_to_mysql(config)
        if conn is None:
            flash("No se pudo conectar a la BDA")
            return render_template("registro.html")
        
        cursor = conn.cursor()
        use_database(conn, cursor, DB_NAME)

        # Verificar si el usuario ya existe
        sql_check = "SELECT usuario FROM usuarios WHERE usuario = %s"
        cursor.execute(sql_check, (usuario,))
        usuario_existente = cursor.fetchone()

        if usuario_existente:
            flash("El usuario ya existe. Por favor, elige otro nombre de usuario.")
            cursor.close()
            conn.close()
            return render_template("registro.html")

        # Si no existe, crear el nuevo usuario con contraseña hasheada
        password_hash = generate_password_hash(password)
        sql_insert = "INSERT INTO usuarios (usuario, password) VALUES (%s, %s)"
        
        try:
            cursor.execute(sql_insert, (usuario, password_hash))
            conn.commit()
            flash("Registro exitoso. Por favor, inicia sesión.")
            cursor.close()
            conn.close()
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Error al registrar el usuario: {str(e)}")
            cursor.close()
            conn.close()
            return render_template("registro.html")

    return render_template("registro.html")

############################################
#                 ALUMNOS                  #
############################################


# ruta '/alumnos': lista alumnos y ofrece CRUD
@app.route('/alumnos')
@login_required
def alumnos():
    conn = connect_to_mysql(config)
    if conn is None:
        flash("No se pudo conectar a la BDA")
        return redirect(url_for('login'))
    cursor = conn.cursor(dictionary=True) # devuelve list[dict]
    use_database(conn, cursor, DB_NAME)
    cursor.execute("SELECT * FROM alumnos")
    alumnos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("alumnos.html", alumnos=alumnos)

# Crear alumno
@app.route('/nuevo_alumno', methods=['GET', 'POST'])
@login_required
def nuevo_alumno():
    # Cuando le damos al botón guardar desde alumnos_nuevo.html(POST)
    if request.method == 'POST':
        expediente = request.form['expediente']
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']

        conn = connect_to_mysql(config)
        if conn is None:
            flash("No se pudo conectar a la BDA")
            return redirect(url_for('login'))
        cursor = conn.cursor()
        use_database(conn, cursor, DB_NAME)
        sql = "INSERT INTO alumnos (expediente, nombre, apellidos) VALUES (%s, %s, %s)"
        cursor.execute(sql, (expediente, nombre, apellidos))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('alumnos'))
    # Cuando entramos por URL 127.0.0.1:5000/nuevo_alumno (GET)
    return render_template("alumnos_nuevo.html")

# Editar alumno: pasamos como parámetro el expediente
@app.route('/editar_alumno/<expediente>', methods=['GET', 'POST'])
@login_required
def editar_alumno(expediente):
    conn = connect_to_mysql(config)
    if conn is None:
        flash("No se pudo conectar a la BDA")
        return redirect(url_for('login'))
    cursor = conn.cursor(dictionary=True)
    use_database(conn, cursor, DB_NAME)

    # Cuando le damos al botón Actualizar desde alumnos_editar.html
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']

        sql = "UPDATE alumnos SET nombre=%s, apellidos=%s WHERE expediente=%s"
        cursor.execute(sql, (nombre, apellidos, expediente))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('alumnos'))

    # venimos de la URL 127.0.0.1:5000/editar_alumno/<expediente> (GET)
    cursor.execute("SELECT * FROM alumnos WHERE expediente=%s", (expediente,))
    alumno = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("alumnos_editar.html", alumno=alumno)

# Eliminar alumno: se pasa como parámetro el expediente
@app.route('/eliminar_alumno/<expediente>')
@login_required
def eliminar_alumno(expediente):
    conn = connect_to_mysql(config)
    if conn is None:
        flash("No se pudo conectar a la BDA")
        return redirect(url_for('login'))
    cursor = conn.cursor()
    use_database(conn, cursor, DB_NAME)

    cursor.execute("DELETE FROM alumnos WHERE expediente=%s", (expediente,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('alumnos'))

############################################
#                 MODULOS                  #
############################################

# ruta '/modulos': lista modulos y ofrece CRUD
@app.route('/modulos')
@login_required
def modulos():
    conn = connect_to_mysql(config)
    if conn is None:
        flash("No se pudo conectar a la BDA")
        return redirect(url_for('login'))
    cursor = conn.cursor(dictionary=True) # devuelve list[dict]
    use_database(conn, cursor, DB_NAME)
    cursor.execute("SELECT * FROM modulos")
    modulos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("modulos.html", modulos=modulos)

# Crear modulo
@app.route('/nuevo_modulo', methods=['GET', 'POST'])
@login_required
def nuevo_modulo():
    if request.method == 'POST':
        codigo = request.form['codigo']
        nombre = request.form['nombre']

        conn = connect_to_mysql(config)
        if conn is None:
            flash("No se pudo conectar a la BDA")
            return redirect(url_for('login'))
        cursor = conn.cursor()
        use_database(conn, cursor, DB_NAME)
        sql = "INSERT INTO modulos (codigo, nombre) VALUES (%s, %s)"
        cursor.execute(sql, (codigo, nombre))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('modulos'))
    return render_template("modulos_nuevo.html")

# Editar modulo: pasamos como parámetro el codigo
@app.route('/editar_modulo/<codigo>', methods=['GET', 'POST'])
@login_required
def editar_modulo(codigo):
    conn = connect_to_mysql(config)
    if conn is None:
        flash("No se pudo conectar a la BDA")
        return redirect(url_for('login'))
    cursor = conn.cursor(dictionary=True)
    use_database(conn, cursor, DB_NAME)

    if request.method == 'POST':
        nombre = request.form['nombre']

        sql = "UPDATE modulos SET nombre=%s WHERE codigo=%s"
        cursor.execute(sql, (nombre, codigo))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('modulos'))

    cursor.execute("SELECT * FROM modulos WHERE codigo=%s", (codigo,))
    modulo = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("modulos_editar.html", modulo=modulo)

# Eliminar modulo: se pasa como parámetro el codigo
@app.route('/eliminar_modulo/<codigo>')
@login_required
def eliminar_modulo(codigo):
    conn = connect_to_mysql(config)
    if conn is None:
        flash("No se pudo conectar a la BDA")
        return redirect(url_for('login'))
    cursor = conn.cursor()
    use_database(conn, cursor, DB_NAME)

    cursor.execute("DELETE FROM modulos WHERE codigo=%s", (codigo,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('modulos'))

############################################
#                   NOTAS                  #
############################################

# ruta '/notas': lista notas y ofrece CRUD
@app.route('/notas')
@login_required
def notas():
    conn = connect_to_mysql(config)
    if conn is None:
        flash("No se pudo conectar a la BDA")
        return redirect(url_for('login'))
    cursor = conn.cursor(dictionary=True) # devuelve list[dict]
    use_database(conn, cursor, DB_NAME)
    cursor.execute("SELECT * FROM notas")
    notas = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("notas.html", notas=notas)

# Crear nota
@app.route('/notas_nueva', methods=['GET', 'POST'])
@login_required
def nueva_nota():
    if request.method == 'POST':
        expediente = request.form['expediente']
        codigo = request.form['codigo']
        nota = request.form['nota']

        conn = connect_to_mysql(config)
        if conn is None:
            flash("No se pudo conectar a la BDA")
            return redirect(url_for('login'))
        cursor = conn.cursor()
        use_database(conn, cursor, DB_NAME)
        sql = "INSERT INTO notas (expediente, codigo, nota) VALUES (%s, %s, %s)"
        cursor.execute(sql, (expediente, codigo, nota))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('notas'))
    return render_template("notas_nueva.html")

# Editar nota: pasamos como parámetro el expediente y el codigo
@app.route('//<expediente>/<codigo>', methods=['GET', 'POST'])
@login_required
def editar_nota(expediente, codigo):
    conn = connect_to_mysql(config)
    if conn is None:
        flash("No se pudo conectar a la BDA")
        return redirect(url_for('login'))
    cursor = conn.cursor(dictionary=True)
    use_database(conn, cursor, DB_NAME)

    if request.method == 'POST':
        nota = request.form['nota']

        sql = "UPDATE notas SET nota=%s WHERE expediente=%s AND codigo=%s"
        cursor.execute(sql, (nota, expediente, codigo))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('notas'))

    cursor.execute("SELECT * FROM notas WHERE expediente=%s AND codigo=%s", (expediente, codigo))
    nota = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("notas_editar.html", nota=nota)

# Eliminar nota: se pasa como parámetro el expediente y el codigo
@app.route('/eliminar_nota/<expediente>/<codigo>')
@login_required
def eliminar_nota(expediente, codigo):
    conn = connect_to_mysql(config)
    if conn is None:
        flash("No se pudo conectar a la BDA")
        return redirect(url_for('login'))
    cursor = conn.cursor()
    use_database(conn, cursor, DB_NAME)

    cursor.execute("DELETE FROM notas WHERE expediente=%s AND codigo=%s", (expediente, codigo))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('notas'))


if __name__ == '__main__':
    app.run(debug=True)
