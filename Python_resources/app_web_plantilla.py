from flask import Flask, render_template, request, redirect, url_for
from conectar_logger import connect_to_mysql
from config import config # Aquí debes poner tu configuración de acceso a la BDA
from DA_plantilla_alumnos import use_database

# para la seguridad básica
from flask import session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = "Me_Gusta_Python" # Necesario para sesiones

DB_NAME = config["database"] # Aquí pon tu BDA

############################################
#          SEGURIDAD (MUY BÁSICA)          #
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

        # EJEMPLO: usuario almacenado en el código.
        if usuario == "admin" and password == "1234":
            session["usuario"] = usuario
            return redirect(url_for("inicio"))
        else:
            flash("Usuario o contraseña incorrectos")

    return render_template("login.html")


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
        creditos = request.form['creditos']

        conn = connect_to_mysql(config)
        if conn is None:
            flash("No se pudo conectar a la BDA")
            return redirect(url_for('login'))
        cursor = conn.cursor()
        use_database(conn, cursor, DB_NAME)
        sql = "INSERT INTO modulos (codigo, nombre, creditos) VALUES (%s, %s, %s)"
        cursor.execute(sql, (codigo, nombre, creditos))
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
        creditos = request.form['creditos']

        sql = "UPDATE modulos SET nombre=%s, creditos=%s WHERE codigo=%s"
        cursor.execute(sql, (nombre, creditos, codigo))
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
@app.route('/nuevo_nota', methods=['GET', 'POST'])
@login_required
def nuevo_nota():
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
@app.route('/editar_nota/<expediente>/<codigo>', methods=['GET', 'POST'])
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
