import streamlit as st
from src.configuracion import COLOR_TITULO, COLOR_BOTON, COLOR_HOVER, COLOR_SIDEBAR

CSS_BASE = f"""
<style>
#MainMenu, footer {{visibility: hidden;}}
h1, h2, h3 {{color: {COLOR_TITULO};}}

/* Tarjetas identificadas con claves propias de la aplicacion. */
[class*="st-key-tarjeta_"] {{
    background: #FFFFFF; border-radius: 14px;
    border: 1px solid rgba(18, 84, 79, .10);
    box-shadow: 0 3px 12px rgba(18, 84, 79, .04);
}}

/* Botones */
.stButton button, .stFormSubmitButton button, .stDownloadButton button {{
    background: {COLOR_BOTON}; color: white; border: none; font-weight: 600;
}}
.stButton button:hover, .stFormSubmitButton button:hover,
.stDownloadButton button:hover {{
    background: {COLOR_HOVER}; color: white; border: none;
}}
.stButton button:disabled {{ background: #AAAAAA; color: white; }}

/* Menú lateral oscuro */
[data-testid="stSidebar"] {{ background: {COLOR_SIDEBAR}; }}
[data-testid="stSidebar"] * {{ color: #D7E8E6; }}
[data-testid="stSidebar"] .stButton button {{
    background: transparent; border: 1px solid #D7E8E6;
}}
[data-testid="stSidebar"] .stButton button:hover {{ background: #186862; }}
[data-testid="stSidebar"] .st-key-cerrar_sesion button {{
    min-height: 2.8rem;
    padding: .65rem 1rem;
    border: 1px solid rgba(215, 232, 230, .25);
    border-radius: 10px;
    background: rgba(215, 232, 230, .06);
    transition: background .15s ease, border-color .15s ease;
}}
[data-testid="stSidebar"] .st-key-cerrar_sesion button:hover {{
    background: rgba(215, 232, 230, .14);
    border-color: rgba(215, 232, 230, .55);
}}
[data-testid="stSidebar"] .st-key-cerrar_sesion button:focus-visible {{
    outline: 2px solid #D7E8E6;
    outline-offset: 3px;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    padding: .65rem .8rem; border-radius: 8px; width: 100%;
    box-sizing: border-box;
}}
[data-testid="stSidebar"] [data-testid="stRadioGroup"] {{ align-items: stretch; }}
/* Ocultar solo el círculo visual; conservar el control accesible y su texto. */
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child {{
    display: none;
}}
[data-testid="stSidebar"] [data-testid="stRadioOption"]:hover {{
    background: rgba(215, 232, 230, .07);
}}
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-focus-visible] {{
    outline: 2px solid #D7E8E6; outline-offset: 2px;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
    background: rgba(215, 232, 230, .12);
}}

/* Métricas y títulos del dashboard */
[data-testid="stMetricValue"] {{ color: {COLOR_BOTON}; }}
[data-testid="stMetricLabel"] {{ color: #536967; }}
h1 {{ letter-spacing: -.025em; }}
h3 {{ font-weight: 600; }}
</style>
"""


def aplicar_estilos() -> None:
    st.markdown(CSS_BASE, unsafe_allow_html=True)
