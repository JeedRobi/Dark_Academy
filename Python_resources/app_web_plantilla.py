from flask import Flask, render_template, request, redirect, url_for
from conectar_logger import connect_to_mysql
from config import config # Aquí debes poner tu configuración de acceso a la BDA
from DA_solución import use_database

# para la seguridad básica
from flask import session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = "Me_Gusta_Python" # Necesario para sesiones

DB_NAME = "Dark_Academy_Natxo" # Aquí pon tu BDA

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
    cursor = conn.cursor(dictionary=True) # devuelve list[dict]
    use_database(cursor, DB_NAME)
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
        cursor = conn.cursor()
        use_database(cursor, DB_NAME)
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
    cursor = conn.cursor(dictionary=True)
    use_database(cursor, DB_NAME)

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
    cursor = conn.cursor()
    use_database(cursor, DB_NAME)

    cursor.execute("DELETE FROM alumnos WHERE expediente=%s", (expediente,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('alumnos'))

############################################
#                 MODULOS                  #
############################################

# ruta '/modulos': lista modulos y ofrece CRUD


# Crear modulo


# Editar modulo: pasamos como parámetro el codigo


# Eliminar modulo: se pasa como parámetro el codigo

############################################
#                   NOTAS                  #
############################################

# ruta '/notas': lista notas y ofrece CRUD

# Crear nota

# Editar nota: pasamos como parámetro el expediente y el codigo

# Eliminar nota: se pasa como parámetro el expediente y el codigo


if __name__ == '__main__':
    app.run(debug=True)
