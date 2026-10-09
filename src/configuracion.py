"""Rutas del proyecto, independientes de la carpeta de ejecución."""

from pathlib import Path

DIRECTORIO_PROYECTO = Path(__file__).resolve().parent.parent

# Desactivar al terminar las pruebas para recuperar el inicio de sesión normal.
MODO_DESARROLLO = False

RUTA_CSV = DIRECTORIO_PROYECTO / "datos" / "registro_pacientes.csv"

MODELOS = {
    "CNN": DIRECTORIO_PROYECTO / "modelos" / "modelo_cnn.keras",
    "ResNet50": DIRECTORIO_PROYECTO / "modelos" / "modelo_resnet.keras",
    "EfficientNetB0": DIRECTORIO_PROYECTO / "modelos" / "modelo_efficientnet.keras",
}

COLOR_TITULO = "#12544F"

COLOR_BOTON = "#186862"

COLOR_HOVER = "#2A835F"

COLOR_SIDEBAR = "#12544F"

CLASES = ["glioma", "meningioma", "notumor", "pituitary"]

NOMBRES_CLASES = {
    "glioma": "Glioma",
    "meningioma": "Meningioma",
    "notumor": "Sin tumor",
    "pituitary": "Tumor pituitario",
}

TAM_ENTRADA = (224, 224)
