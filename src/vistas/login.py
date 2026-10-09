import streamlit as st


def obtener_credenciales() -> tuple[str, str]:
    """Lee el acceso local sin incorporar credenciales al código."""
    try:
        acceso = st.secrets["acceso"]
        usuario = acceso["usuario"]
        contrasena = acceso["contrasena"]
    except (FileNotFoundError, KeyError, st.errors.StreamlitSecretNotFoundError) as exc:
        raise ValueError(
            "Configura el acceso en .streamlit/secrets.toml usando el archivo de ejemplo."
        ) from exc
    if not isinstance(usuario, str) or not isinstance(contrasena, str) or not usuario or not contrasena:
        raise ValueError("El usuario y la contraseña de secrets.toml deben ser textos no vacíos.")
    return usuario, contrasena

def pantalla_login() -> None:
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        st.write("")
        st.write("")
        with st.container(border=True, key="tarjeta_login"):
            st.markdown(
                "<h2 style='text-align:center;margin-top:0'>Iniciar sesión</h2>",
                unsafe_allow_html=True,
            )
            with st.form("form_login", border=False):
                usuario = st.text_input("Usuario")
                contrasena = st.text_input("Contraseña", type="password")
                enviado = st.form_submit_button("Iniciar sesión", width="stretch")

            if enviado:
                try:
                    usuario_valido, contrasena_valida = obtener_credenciales()
                except ValueError as exc:
                    st.error(str(exc))
                    return
                if usuario == usuario_valido and contrasena == contrasena_valida:
                    st.session_state.autenticado = True
                    st.session_state.usuario = usuario
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
