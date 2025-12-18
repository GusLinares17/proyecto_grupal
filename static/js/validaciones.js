document.addEventListener("DOMContentLoaded", () => {


    const formLogin = document.querySelector("form[action='/login']");
    const formRegistro = document.querySelector("form[action='/registro']");

    function validarPassword(password) {
        const regex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/;
        return regex.test(password);
    }

    function validarFormulario(e) {
        const inputs = e.target.querySelectorAll("input");

        for (let input of inputs) {
            if (input.value.trim() === "") {
                alert("Todos los campos son obligatorios");
                e.preventDefault();
                return;
            }
        }

        const passwordInput = e.target.querySelector("input[name='password']");
        if (passwordInput) {
            const password = passwordInput.value;

            if (!validarPassword(password)) {
                alert(
                    "La contraseña debe tener mínimo 6 caracteres, " +
                    "al menos una letra y un número"
                );
                e.preventDefault();
                return;
            }
        }
    }

    if (formLogin) {
        formLogin.addEventListener("submit", validarFormulario);
    }

    if (formRegistro) {
        formRegistro.addEventListener("submit", validarFormulario);
    }
    

    const botonesEliminar = document.querySelectorAll(".btn-eliminar");

    botonesEliminar.forEach(boton => {
        boton.addEventListener("click", function (e) {
            if (!confirm("¿Seguro que deseas cancelar esta cita?")) {
                e.preventDefault();
            }
        });
    });


    const inputFecha = document.querySelector("input[type='date']");
    const mensajeFecha = document.getElementById("mensaje-fecha");

    if (inputFecha && mensajeFecha) {
        inputFecha.addEventListener("change", () => {
            mensajeFecha.textContent = "Fecha seleccionada correctamente";
        });
    }

});
