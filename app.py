from flask import Flask, render_template, request, redirect, url_for, session
from database import get_connection
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave_secreta_simple"

# ---------- RUTAS PRINCIPALES ----------

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id_usuario, nombre, rol FROM usuarios WHERE correo=%s AND contrasena=%s",
            (correo, password)
        )

        usuario = cursor.fetchone()

        cursor.close()
        conexion.close()

        if usuario:
            session["id_usuario"] = usuario[0]
            session["nombre"] = usuario[1]
            session["rol"] = usuario[2]

            # REDIRECCIÓN SEGÚN ROL
            if usuario[2] == "admin":
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("cita"))
        else:
            return render_template(
                "login.html",
                error="Correo o contraseña incorrectos"
            )

    return render_template("login.html")



# ---------- REGISTRO ----------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, contrasena, rol) VALUES (%s, %s, %s, %s)",
            (nombre, correo, password, "paciente")
        )

        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect(url_for("login"))

    return render_template("registro.html")


# ---------- CITAS ----------
@app.route("/cita", methods=["GET", "POST"])
def cita():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    id_usuario = session["id_usuario"]

    conexion = get_connection()
    cursor = conexion.cursor()

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

    horarios = [
        "09:00", "10:00", "11:00",
        "14:00", "15:00", "16:00", "17:00", "18:00"
    ]

    fecha = request.args.get("fecha")
    ocupados = []

    if fecha:
        cursor.execute(
            "SELECT hora FROM citas WHERE fecha=%s",
            (fecha,)
        )

        for fila in cursor.fetchall():
            hora_db = fila[0]
            if hasattr(hora_db, "strftime"):
                ocupados.append(hora_db.strftime("%H:%M"))
            else:
                total = int(hora_db.total_seconds())
                h = total // 3600
                m = (total % 3600) // 60
                ocupados.append(f"{h:02d}:{m:02d}")

    if request.method == "POST":
        fecha = request.form["fecha"]
        hora = request.form["hora"]

        dia = datetime.strptime(fecha, "%Y-%m-%d").weekday()
        if dia > 4:
            cursor.close()
            conexion.close()
            return render_template(
                "cita.html",
                error="Solo se atiende de lunes a viernes",
                horarios=horarios,
                ocupados=ocupados,
                fecha=fecha
            )

        if hora not in horarios:
            cursor.close()
            conexion.close()
            return render_template(
                "cita.html",
                error="Horario no permitido",
                horarios=horarios,
                ocupados=ocupados,
                fecha=fecha
            )

        cursor.execute(
            "SELECT COUNT(*) FROM citas WHERE fecha=%s AND hora=%s",
            (fecha, hora)
        )

        if cursor.fetchone()[0] > 0:
            cursor.close()
            conexion.close()
            return render_template(
                "cita.html",
                error="Horario ya ocupado",
                horarios=horarios,
                ocupados=ocupados,
                fecha=fecha
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


# ---------- ADMIN ----------
@app.route("/admin")
def admin():

    if "id_usuario" not in session:
        return redirect(url_for("login"))

    if session.get("rol") != "admin":
        return redirect(url_for("inicio"))

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT c.id_cita, c.fecha, c.hora, u.nombre
        FROM citas c
        JOIN usuarios u ON c.id_usuario = u.id_usuario
        ORDER BY c.fecha, c.hora
    """)

    citas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("admin.html", citas=citas)


@app.route("/admin/eliminar/<int:id_cita>")
def eliminar_cita(id_cita):

    if "id_usuario" not in session or session.get("rol") != "admin":
        return redirect(url_for("login"))

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM citas WHERE id_cita=%s",
        (id_cita,)
    )
    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for("admin"))


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio"))


# ---------- EJECUCIÓN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



