import hashlib

from PIL import Image
import numpy as np
import streamlit as st
from src.configuracion import CLASES, MODELOS, TAM_ENTRADA

@st.cache_resource(show_spinner="Cargando modelo…")
def cargar_modelo(nombre_visible: str):
    """Carga el modelo elegido una vez y conserva la huella de su archivo."""
    ruta = MODELOS[nombre_visible]
    if not ruta.is_file():
        raise FileNotFoundError(
            f"No se encontró '{ruta.name}' en {ruta.parent}. "
            "Copia ahí el archivo .keras exportado desde el notebook de entrenamiento."
        )
    import tensorflow as tf

    huella = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            huella.update(bloque)
    modelo = tf.keras.models.load_model(ruta)
    modelo._version_archivo = huella.hexdigest()
    return modelo


def obtener_version_modelo(nombre_visible: str) -> str:
    """Identifica el archivo cargado mediante su SHA-256; reutiliza la caché."""
    return cargar_modelo(nombre_visible)._version_archivo


def validar_probabilidades(salida) -> np.ndarray:
    """Comprueba la salida softmax antes de interpretarla como probabilidades."""
    probabilidades = np.asarray(salida, dtype=np.float64)
    if probabilidades.shape != (len(CLASES),):
        raise ValueError(
            f"El modelo debe devolver {len(CLASES)} probabilidades; "
            f"se recibió una salida con forma {probabilidades.shape}."
        )
    if not np.all(np.isfinite(probabilidades)):
        raise ValueError("El modelo devolvió probabilidades no finitas (NaN o infinito).")
    if np.any(probabilidades < 0) or np.any(probabilidades > 1):
        raise ValueError("El modelo devolvió probabilidades fuera del rango de 0 a 1.")
    if not np.isclose(probabilidades.sum(), 1.0, rtol=0, atol=1e-5):
        raise ValueError("Las probabilidades del modelo no suman aproximadamente 1.")
    return probabilidades


def predecir(nombre_modelo: str, imagen_pil: Image.Image) -> np.ndarray:
    """Ejecuta inferencia RGB sin duplicar la normalización del modelo."""
    import tensorflow as tf

    modelo = cargar_modelo(nombre_modelo)
    arreglo = np.asarray(imagen_pil.convert("RGB"), dtype=np.float32)
    entrada = tf.image.resize(arreglo, TAM_ENTRADA)[tf.newaxis, ...]
    salida = modelo(entrada, training=False).numpy()
    if salida.shape != (1, len(CLASES)):
        raise ValueError(
            f"Se esperaba una salida de forma (1, {len(CLASES)}); "
            f"el modelo devolvió {salida.shape}."
        )
    return validar_probabilidades(salida[0])
