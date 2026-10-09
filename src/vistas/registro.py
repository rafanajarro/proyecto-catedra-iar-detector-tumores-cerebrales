import pandas as pd
import streamlit as st
from src import registro_datos

def pagina_registro() -> None:
    cab, btn = st.columns([5, 1])
    cab.title("Registro de pacientes")
    btn.write("")
    btn.button("Actualizar", key="act_registro")

    try:
        registros = registro_datos.obtener_resultados()
    except registro_datos.ErrorRegistro as exc:
        st.error(str(exc))
        return
    df = pd.DataFrame(registros, columns=registro_datos.COLUMNAS)

    texto = st.text_input("Buscar por nombre o ID", placeholder="Ej. Juan, 12345…").strip().lower()
    if texto:
        mask = (
            df["paciente"].str.lower().str.contains(texto, regex=False, na=False)
            | df["id_paciente"].str.lower().str.contains(texto, regex=False, na=False)
        )
        df = df[mask]

    df = df.rename(columns={
        "fecha_hora": "Fecha y hora", "paciente": "Paciente", "id_paciente": "ID / Expediente",
        "modelo": "Modelo", "prediccion": "Resultado", "confianza": "Confianza",
        "archivo_imagen": "Imagen",
        "id_analisis": "ID de análisis", "huella_imagen": "Huella de imagen",
        "version_modelo": "Versión del modelo",
    })
    tabla = df.copy()
    tabla["Confianza"] = tabla["Confianza"] * 100
    st.dataframe(
        tabla.iloc[::-1], width="stretch", hide_index=True,
        column_config={
            "Confianza": st.column_config.NumberColumn("Confianza", format="%.1f%%"),
            "Huella de imagen": None, "Versión del modelo": None,
        },
    )  # más recientes primero; el CSV exportado conserva la proporción numérica
    st.download_button(
        "Descargar CSV", df.to_csv(index=False).encode("utf-8"),
        file_name="registro_pacientes.csv", mime="text/csv",
    )
