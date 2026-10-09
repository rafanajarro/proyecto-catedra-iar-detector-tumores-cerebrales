"""Lectura de imágenes convencionales y DICOM para la consola.

Los DICOM monocromáticos se convierten a RGB de 8 bits tras aplicar
escala de modalidad y ventana/VOI disponibles. Se usa el corte central
en archivos multiframe; no se realiza un análisis del volumen completo.
"""
import numpy as np
import pydicom
from PIL import Image
from pydicom.pixels import apply_modality_lut, apply_voi_lut


def cargar_imagen(archivo) -> Image.Image:
    """Abre el archivo desde el inicio y devuelve una imagen RGB."""
    archivo.seek(0)
    if not archivo.name.lower().endswith(".dcm"):
        return Image.open(archivo).convert("RGB")
    return cargar_dicom(archivo)


def cargar_dicom(archivo) -> Image.Image:
    """Lee DICOM MONOCHROME1/2 o RGB con metadatos de píxeles coherentes."""
    ds = pydicom.dcmread(archivo)
    if not any(campo in ds for campo in ("PixelData", "FloatPixelData", "DoubleFloatPixelData")):
        raise ValueError("El archivo DICOM no contiene una imagen de píxeles.")
    fotometria = getattr(ds, "PhotometricInterpretation", "")
    muestras = int(getattr(ds, "SamplesPerPixel", 0))
    if (fotometria, muestras) not in (("MONOCHROME1", 1), ("MONOCHROME2", 1), ("RGB", 3)):
        raise ValueError(f"Formato DICOM no soportado: {fotometria or 'sin fotometría'}.")
    # Los DICOM mejorados requieren interpretar transformaciones por frame.
    if "PerFrameFunctionalGroupsSequence" in ds or "SharedFunctionalGroupsSequence" in ds:
        raise ValueError("Los DICOM con grupos funcionales por corte aún no están soportados.")
    cortes = int(getattr(ds, "NumberOfFrames", 1))
    filas = int(getattr(ds, "Rows", 0))
    columnas = int(getattr(ds, "Columns", 0))
    if cortes < 1 or filas < 1 or columnas < 1:
        raise ValueError("Las dimensiones o el número de cortes DICOM no son válidos.")
    try:
        pixeles = ds.pixel_array
    except Exception as exc:
        raise ValueError(
            "No se pudieron decodificar los píxeles DICOM. "
            "El archivo puede estar dañado o necesitar un decodificador para su compresión."
        ) from exc
    forma_corte = (filas, columnas) if muestras == 1 else (filas, columnas, 3)
    forma_esperada = (cortes, *forma_corte) if cortes > 1 else forma_corte
    if pixeles.shape != forma_esperada:
        raise ValueError("Los píxeles DICOM no coinciden con las dimensiones declaradas.")
    if cortes > 1:
        pixeles = pixeles[cortes // 2]
    if muestras == 3:
        if pixeles.dtype != np.uint8:
            raise ValueError("Solo se admiten DICOM RGB de 8 bits por canal.")
        return Image.fromarray(pixeles).convert("RGB")
    pixeles = apply_modality_lut(pixeles, ds)
    pixeles = apply_voi_lut(pixeles, ds)
    valores = np.asarray(pixeles, dtype=np.float64)
    if not np.all(np.isfinite(valores)):
        raise ValueError("La imagen DICOM contiene valores no finitos.")
    minimo, maximo = valores.min(), valores.max()
    if maximo == minimo:
        raise ValueError("La imagen DICOM es uniforme y no permite un análisis de contraste.")
    imagen = np.rint((valores - minimo) / (maximo - minimo) * 255).astype(np.uint8)
    if fotometria == "MONOCHROME1":
        imagen = 255 - imagen
    return Image.fromarray(imagen).convert("RGB")
