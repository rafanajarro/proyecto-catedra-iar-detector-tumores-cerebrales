"""Entrada de MRI Console. Ejecutar con: streamlit run app.py."""
import streamlit as st
from src.configuracion import MODO_DESARROLLO
from src.estilos import aplicar_estilos
from src.vistas.login import pantalla_login
from src.vistas.consola import pagina_consola
from src.vistas.dashboard import pagina_dashboard
from src.vistas.registro import pagina_registro

st.set_page_config(
    page_title="MRI Console",
    page_icon="🧠",
    layout="wide",
)


aplicar_estilos()
st.session_state.setdefault("autenticado", False)
st.session_state.setdefault("usuario", "")
st.session_state.setdefault("resultado", None)
st.session_state.setdefault("acceso_desarrollo", False)

if MODO_DESARROLLO:
    st.session_state.autenticado = True
    st.session_state.usuario = "desarrollo"
    st.session_state.acceso_desarrollo = True
elif st.session_state.acceso_desarrollo:
    st.session_state.autenticado = False
    st.session_state.usuario = ""
    st.session_state.resultado = None
    st.session_state.acceso_desarrollo = False

PAGINAS = {
    "Consola MRI": pagina_consola,
    "Dashboard": pagina_dashboard,
    "Registro de pacientes": pagina_registro,
}


def aplicacion() -> None:
    with st.sidebar:
        st.markdown("### MRI Console")
        st.caption("Análisis de resonancias")
        eleccion = st.radio("Menú", list(PAGINAS.keys()), label_visibility="collapsed")
        if not MODO_DESARROLLO:
            st.divider()
        if not MODO_DESARROLLO and st.button(
            "Cerrar sesión", icon=":material/logout:", key="cerrar_sesion", width="stretch"
        ):
            st.session_state.autenticado = False
            st.session_state.usuario = ""
            st.session_state.resultado = None
            st.rerun()

    PAGINAS[eleccion]()


if st.session_state.autenticado:
    aplicacion()
else:
    pantalla_login()
