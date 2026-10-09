import hashlib
from uuid import uuid4

import numpy as np
import streamlit as st
from src import registro_datos
from src.configuracion import CLASES, NOMBRES_CLASES, MODELOS, COLOR_BOTON
from src.inferencia import predecir, obtener_version_modelo
from src.imagenes import cargar_imagen

def pagina_consola() -> None:
    st.title("Panel de análisis de resonancias")
    col_img, col_ctrl = st.columns([1, 1.2], gap="large")

    with col_img:
        with st.container(border=True, key="tarjeta_imagen"):
            st.subheader("Imagen a analizar")
            archivo = st.file_uploader(
                "Cargar imagen", type=["jpg", "jpeg", "png", "bmp", "dcm"], label_visibility="collapsed"
            )
            huella_imagen = (
                hashlib.sha256(archivo.getbuffer()).hexdigest()
                if archivo is not None else None
            )
            resultado_anterior = st.session_state.resultado
            if (
                resultado_anterior is not None
                and resultado_anterior.get("huella_imagen") != huella_imagen
            ):
                st.session_state.resultado = None
            imagen = None
            if archivo is not None:
                try:
                    imagen = cargar_imagen(archivo)
                    if archivo.name.lower().endswith(".dcm"):
                        st.image(imagen, caption="Imagen DICOM procesada", width=400)
                    else:
                        st.image(imagen, width="stretch", caption=archivo.name)
                except Exception as e:
                    imagen = None
                    st.error(f"No se pudo abrir el archivo seleccionado como imagen: {e}")


    with col_ctrl:
        with st.container(border=True, key="tarjeta_analisis"):
            st.subheader("Datos del paciente")
            paciente = st.text_input("Nombre completo")
            id_paciente = st.text_input("ID / Expediente")
            paciente_actual = paciente.strip()
            expediente_actual = id_paciente.strip()
            resultado_anterior = st.session_state.resultado
            if (
                resultado_anterior is not None
                and (
                    resultado_anterior.get("paciente") != paciente_actual
                    or resultado_anterior.get("id_paciente") != expediente_actual
                )
            ):
                st.session_state.resultado = None

            st.subheader("Modelo de IA")
            modelo = st.selectbox(
                "Modelo", list(MODELOS.keys()), index=None,
                placeholder="Selecciona un modelo", label_visibility="collapsed",
            )

            st.caption(
                "Cada análisis completado se guarda como un registro nuevo, "
                "aunque repitas la misma imagen, paciente y modelo."
            )
            if st.button("Analizar imagen", width="stretch"):
                # Cada intento reemplaza el resultado anterior, incluso si falla.
                st.session_state.resultado = None
                if modelo is None:
                    st.warning("Selecciona un modelo de IA antes de analizar.")
                elif imagen is None:
                    st.warning("Primero carga una resonancia para analizar.")
                elif not paciente_actual:
                    st.warning("Escribe el nombre del paciente antes de analizar.")
                else:
                    try:
                        with st.spinner("Analizando imagen…"):
                            probs = predecir(modelo, imagen)
                            version_modelo = obtener_version_modelo(modelo)
                    except ImportError:
                        st.error("TensorFlow no está instalado: pip install tensorflow")
                    except FileNotFoundError as e:
                        st.error(str(e))
                    except Exception as e:
                        st.error(f"Error durante el análisis: {e}")
                    else:
                        i = int(np.argmax(probs))
                        confianza = float(probs[i])
                        id_analisis = str(uuid4())
                        st.session_state.resultado = {
                            "archivo": archivo.name,
                            "huella_imagen": huella_imagen,
                            "paciente": paciente_actual,
                            "id_paciente": expediente_actual,
                            "modelo": modelo,
                            "probs": probs.tolist(),
                            "clase": NOMBRES_CLASES[CLASES[i]],
                            "confianza": confianza,
                            "id_analisis": id_analisis,
                            "version_modelo": version_modelo,
                        }
                        try:
                            registro_datos.guardar_resultado(
                                paciente=paciente, id_paciente=id_paciente, modelo=modelo,
                                prediccion=NOMBRES_CLASES[CLASES[i]], confianza=confianza,
                                archivo_imagen=archivo.name,
                                huella_imagen=huella_imagen, version_modelo=version_modelo,
                                id_analisis=id_analisis,
                            )
                        except Exception as e:
                            st.warning(f"El análisis terminó, pero no se pudo guardar el registro: {e}")
                        else:
                            st.success("Análisis guardado como un registro nuevo.")

            st.divider()
            st.subheader("Resultado")

            res = st.session_state.resultado
            # Solo se muestra si corresponde a la imagen, modelo y paciente actuales
            vigente = (
                res is not None and imagen is not None
                and res.get("huella_imagen") == huella_imagen
                and res["modelo"] == modelo
                and res.get("paciente") == paciente_actual
                and res.get("id_paciente") == expediente_actual
            )
            if vigente:
                st.caption(
                    f"Paciente: {res['paciente']} · Expediente: {res['id_paciente'] or 'Sin expediente'}"
                )
                st.markdown(
                    f"<div style='font-size:1.6rem;font-weight:700;color:{COLOR_BOTON}'>{res['clase']}</div>",
                    unsafe_allow_html=True,
                )
                st.caption(f"Modelo: {res['modelo']}  ·  Confianza: {res['confianza'] * 100:.1f}%")
                for clase, p in zip(CLASES, res["probs"]):
                    st.progress(min(max(p, 0.0), 1.0), text=f"{NOMBRES_CLASES[clase]} — {p * 100:.0f}%")
            else:
                st.markdown("—")
                st.caption("Carga una imagen y presiona Analizar")
