"""Almacenamiento simple (CSV) de los resultados de análisis por paciente.
Lo usan tanto la consola MRI (para guardar) como el Dashboard y el Registro
de pacientes (para leer)."""

import os
import csv
import math
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4
from datetime import datetime

from src.configuracion import RUTA_CSV

COLUMNAS_ANTERIORES = ["fecha_hora", "paciente", "id_paciente", "modelo", "prediccion", "confianza", "archivo_imagen"]
COLUMNAS = COLUMNAS_ANTERIORES + ["id_analisis", "huella_imagen", "version_modelo"]


class ErrorRegistro(Exception):
    """El registro no puede consultarse o tiene un formato inválido."""


def normalizar_confianza(valor: str | float) -> float:
    """Devuelve una proporción 0-1; admite porcentajes de registros antiguos."""
    texto = str(valor).strip()
    try:
        confianza = float(texto[:-1]) / 100 if texto.endswith("%") else float(texto)
    except (ValueError, TypeError) as exc:
        raise ValueError("La confianza debe ser un número entre 0 y 1 o un porcentaje válido.") from exc
    if not math.isfinite(confianza) or not 0 <= confianza <= 1:
        raise ValueError("La confianza debe estar entre 0 y 1.")
    return confianza


def _validar_encabezado(lector):
    if lector.fieldnames not in (COLUMNAS, COLUMNAS_ANTERIORES):
        raise ErrorRegistro(
            "El registro está vacío o tiene columnas incorrectas. "
            "Revisa el encabezado de datos/registro_pacientes.csv; no se modificó el archivo."
        )


def _asegurar_archivo() -> None:
    if not os.path.exists(RUTA_CSV):
        RUTA_CSV.parent.mkdir(parents=True, exist_ok=True)
        with open(RUTA_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(COLUMNAS)
    with open(RUTA_CSV, newline="", encoding="utf-8-sig") as f:
        _validar_encabezado(csv.DictReader(f, strict=True))


def _actualizar_formato() -> None:
    """Amplía el CSV antiguo con respaldo y reemplazo atómico."""
    with open(RUTA_CSV, newline="", encoding="utf-8-sig") as f:
        encabezado = csv.DictReader(f).fieldnames
    if encabezado == COLUMNAS:
        return
    registros = obtener_resultados()
    respaldo = RUTA_CSV.with_name(f"{RUTA_CSV.stem}.respaldo-{uuid4().hex}.csv")
    shutil.copy2(RUTA_CSV, respaldo)
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", newline="", encoding="utf-8",
                                         dir=RUTA_CSV.parent, delete=False) as f:
            temporal = Path(f.name)
            escritor = csv.DictWriter(f, fieldnames=COLUMNAS)
            escritor.writeheader()
            for registro in registros:
                registro["id_analisis"] = str(uuid4())
                escritor.writerow(registro)
        os.replace(temporal, RUTA_CSV)
    finally:
        if temporal is not None and temporal.exists():
            temporal.unlink()


def guardar_resultado(paciente, id_paciente, modelo, prediccion, confianza, archivo_imagen="",
                      huella_imagen="", version_modelo="", id_analisis=None):
    """Agrega una fila nueva al registro. `confianza` se espera como proporción 0-1."""
    confianza = normalizar_confianza(confianza)
    _asegurar_archivo()
    _actualizar_formato()
    fila = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        paciente.strip() if paciente else "(sin nombre)",
        id_paciente.strip() if id_paciente else "-",
        modelo,
        prediccion,
        confianza,
        os.path.basename(archivo_imagen) if archivo_imagen else "",
        id_analisis or str(uuid4()),
        huella_imagen,
        version_modelo,
    ]
    with open(RUTA_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(fila)
    return fila


def obtener_resultados() -> list[dict[str, str | float]]:
    """Devuelve todos los registros como lista de diccionarios."""
    try:
        _asegurar_archivo()
        with open(RUTA_CSV, newline="", encoding="utf-8-sig") as f:
            lector = csv.DictReader(f, strict=True)
            _validar_encabezado(lector)
            registros = []
            for fila in lector:
                if None in fila or any(valor is None for valor in fila.values()):
                    raise ErrorRegistro(
                        f"El registro contiene una fila incompleta o con columnas adicionales "
                        f"cerca de la línea {lector.line_num}."
                    )
                try:
                    fila["confianza"] = normalizar_confianza(fila["confianza"])
                except ValueError as exc:
                    raise ErrorRegistro(
                        f"La confianza del registro cerca de la línea {lector.line_num} no es válida."
                    ) from exc
                for columna in COLUMNAS[len(COLUMNAS_ANTERIORES):]:
                    fila.setdefault(columna, "")
                registros.append(fila)
            return registros
    except PermissionError as exc:
        raise ErrorRegistro("No se puede acceder al registro. Revisa los permisos del archivo.") from exc
    except (UnicodeError, csv.Error) as exc:
        raise ErrorRegistro("No se puede leer el registro. Revisa su formato CSV y codificación UTF-8.") from exc
    except OSError as exc:
        raise ErrorRegistro("No se pudo abrir el registro de pacientes. Revisa la carpeta datos.") from exc
