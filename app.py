from flask import Flask, render_template, request, redirect, url_for
from database import get_connection
from datetime import datetime



app = Flask(__name__)

# ---------- RUTAS PRINCIPALES ----------

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")

@app.route("/login")
def login():
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



from flask import request

@app.route("/cita", methods=["GET", "POST"])
def cita():
    horarios = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    fecha = request.args.get("fecha")
    ocupados = []

    conn = get_connection()
    cursor = conn.cursor()

    # SI SE ENVÍA UNA FECHA → CARGAR HORARIOS OCUPADOS
    if fecha:
        cursor.execute(
            "SELECT hora FROM citas WHERE fecha = %s",
            (fecha,)
        )
        ocupados = [
    f"{int(h[0].seconds//3600):02d}:{int((h[0].seconds%3600)//60):02d}"
    for h in cursor.fetchall()
]


    # SI SE PRESIONA UN BOTÓN DE HORA
    if request.method == "POST":
        fecha = request.form["fecha"]
        hora = request.form["hora"]

        cursor.execute(
            "SELECT COUNT(*) FROM citas WHERE fecha = %s AND hora = %s",
            (fecha, hora)
        )
        ocupado = cursor.fetchone()[0]

        if ocupado == 0:
            cursor.execute(
                "INSERT INTO citas (id_usuario, id_odontologo, fecha, hora, estado) "
                "VALUES (%s, %s, %s, %s, %s)",
                (2, 1, fecha, hora, "reservada")
            )
            conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("cita", fecha=fecha))

    cursor.close()
    conn.close()

    return render_template(
        "cita.html",
        fecha=fecha,
        horarios=horarios,
        ocupados=ocupados
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

