from collections import Counter
import pandas as pd
import streamlit as st
from src import registro_datos
from src.configuracion import COLOR_BOTON, MODELOS, NOMBRES_CLASES

def pagina_dashboard() -> None:
    cab, btn = st.columns([5, 1], vertical_alignment="center")
    cab.title("Dashboard de resultados")
    cab.caption("Resumen de los análisis registrados y los modelos utilizados.")
    btn.button("Actualizar", width="stretch")

    try:
        registros = registro_datos.obtener_resultados()
    except registro_datos.ErrorRegistro as exc:
        st.error(str(exc))
        return
    conteo_clases = Counter(r["prediccion"] for r in registros)
    conteo_modelos = Counter(r["modelo"] for r in registros)

    confianza = sum(r["confianza"] for r in registros) / len(registros) if registros else None
    metricas = [
        ("Análisis realizados", str(len(registros)), "Cada ejecución guardada cuenta como un análisis."),
        ("Modelos utilizados", str(len(conteo_modelos)), "Modelos distintos con análisis registrados."),
        ("Confianza promedio", f"{confianza:.1%}" if confianza is not None else "—",
         "Promedio de la probabilidad de la clase elegida. No mide la precisión del modelo."),
        ("Resultados sin tumor", str(conteo_clases["Sin tumor"]), "Análisis clasificados como Sin tumor."),
    ]
    for indice, (columna, (titulo, valor, ayuda)) in enumerate(zip(st.columns(4), metricas)):
        with columna.container(border=True, key=f"tarjeta_metrica_{indice}"):
            st.metric(titulo, valor, help=ayuda)

    izquierda, derecha = st.columns([1.3, 1], gap="large")
    with izquierda.container(border=True, key="tarjeta_distribucion"):
        st.subheader("Distribución de resultados")
        st.caption("Cantidad de análisis por clase predicha.")
        if registros:
            nombres = list(NOMBRES_CLASES.values())
            nombres += sorted(set(conteo_clases) - set(nombres))
            df = pd.DataFrame({"Clase": nombres, "Análisis": [conteo_clases[n] for n in nombres]})
            st.bar_chart(df, x="Clase", y="Análisis", color=COLOR_BOTON, horizontal=True)
        else:
            st.info("La distribución aparecerá cuando guardes tu primer análisis.")

    with derecha.container(border=True, key="tarjeta_modelos"):
        st.subheader("Uso de modelos")
        st.caption("Cantidad de análisis realizados con cada modelo.")
        if registros:
            nombres = list(MODELOS)
            nombres += sorted(set(conteo_modelos) - set(nombres))
            df = pd.DataFrame({"Modelo": nombres, "Análisis": [conteo_modelos[n] for n in nombres]})
            st.bar_chart(df, x="Modelo", y="Análisis", color=COLOR_BOTON)
        else:
            st.info("Aquí podrás comparar el uso de CNN, ResNet50 y EfficientNetB0.")

    with st.container(border=True, key="tarjeta_recientes"):
        st.subheader("Últimos análisis")
        st.caption("Los cinco registros más recientes. Consulta el historial completo en Registro de pacientes.")
        if registros:
            recientes = pd.DataFrame(registros[-5:][::-1])
            recientes["confianza"] *= 100
            recientes = recientes.rename(columns={
                "fecha_hora": "Fecha y hora", "paciente": "Paciente", "modelo": "Modelo",
                "prediccion": "Resultado", "confianza": "Confianza",
            })
            st.dataframe(
                recientes[["Fecha y hora", "Paciente", "Modelo", "Resultado", "Confianza"]],
                hide_index=True, width="stretch",
                column_config={"Confianza": st.column_config.NumberColumn(format="%.1f%%")},
            )
        else:
            st.info("Todavía no hay análisis guardados.")
