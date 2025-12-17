from flask import Flask, render_template, request, redirect, url_for, session
from database import get_connection
from datetime import datetime, timedelta



app = Flask(__name__)
app.secret_key = "clave_secreta_simple"

# ---------- RUTAS PRINCIPALES ----------

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id_usuario, nombre, rol FROM usuarios WHERE correo=%s AND contraseña=%s",
            (correo, password)
        )

        usuario = cursor.fetchone()

        cursor.close()
        conexion.close()

        if usuario:
            session["id_usuario"] = usuario[0]
            session["nombre"] = usuario[1]
            session["rol"] = usuario[2]

            return redirect(url_for("cita"))
        else:
            return render_template(
                "login.html",
                error="Correo o contraseña incorrectos"
            )

    return render_template("login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, contraseña, rol) VALUES (%s, %s, %s, %s)",
            (nombre, correo, password, "paciente")
        )

        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect(url_for("login"))

    return render_template("registro.html")




from datetime import datetime, timedelta
from flask import session, request, redirect, url_for, render_template
from database import get_connection

@app.route("/cita", methods=["GET", "POST"])
def cita():

    # SOLO LOGUEADOS
    if "id_usuario" not in session:
        return redirect(url_for("login"))

    id_usuario = session["id_usuario"]

    conexion = get_connection()
    cursor = conexion.cursor()

    # VER SI YA TIENE CITA
    cursor.execute(
        "SELECT fecha, hora FROM citas WHERE id_usuario=%s",
        (id_usuario,)
    )
    cita_usuario = cursor.fetchone()

    if cita_usuario:
        cursor.close()
        conexion.close()
        return render_template(
            "cita.html",
            ya_tiene_cita=True,
            cita=cita_usuario
        )

    # HORARIOS FIJOS
    horarios = [
        "09:00", "10:00", "11:00",
        "14:00", "15:00", "16:00", "17:00", "18:00"
    ]

    fecha = request.args.get("fecha")

    ocupados = []

    # SI YA SE ELIGIÓ FECHA → VER OCUPADOS
    if fecha:
        cursor.execute(
            "SELECT hora FROM citas WHERE fecha=%s",
            (fecha,)
        )
        ocupados = [h[0].strftime("%H:%M") for h in cursor.fetchall()]

    # CUANDO ELIGE HORARIO
    if request.method == "POST":
        fecha = request.form["fecha"]
        hora = request.form["hora"]

        # VALIDAR LUNES A VIERNES
        dia = datetime.strptime(fecha, "%Y-%m-%d").weekday()
        if dia > 4:
            cursor.close()
            conexion.close()
            return render_template(
                "cita.html",
                error="Solo se atiende de lunes a viernes"
            )

        cursor.execute(
            "INSERT INTO citas (id_usuario, fecha, hora) VALUES (%s, %s, %s)",
            (id_usuario, fecha, hora)
        )
        conexion.commit()

        cursor.close()
        conexion.close()
        return redirect(url_for("cita"))

    cursor.close()
    conexion.close()

    return render_template(
        "cita.html",
        horarios=horarios,
        ocupados=ocupados,
        fecha=fecha
    )


@app.route("/admin")
def admin():
    return render_template("admin.html")


# ---------- RUTA DE PRUEBA BD ----------
# ESTA RUTA ES SOLO PARA VERIFICAR CONEXIÓN
@app.route("/test_db")
def test_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM odontologos")
    datos = cursor.fetchall()
    cursor.close()
    conn.close()
    return str(datos)


# ---------- EJECUCIÓN ----------
if __name__ == "__main__":
    app.run(debug=True)

