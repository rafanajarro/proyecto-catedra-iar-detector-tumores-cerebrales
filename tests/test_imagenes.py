import io
import unittest

import numpy as np
from PIL import Image
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid

from src.imagenes import cargar_imagen


def dicom(pixeles, fotometria="MONOCHROME2", cortes=None, **metadatos):
    meta = FileMetaDataset()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    meta.MediaStorageSOPInstanceUID = generate_uid()
    ds = FileDataset(None, {}, file_meta=meta, preamble=b"\0" * 128)
    ds.SOPClassUID = meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
    forma = pixeles.shape[1:] if cortes else pixeles.shape
    ds.Rows, ds.Columns = forma[:2]
    ds.SamplesPerPixel = 3 if fotometria == "RGB" else 1
    ds.PhotometricInterpretation = fotometria
    ds.BitsAllocated = pixeles.dtype.itemsize * 8
    ds.BitsStored = ds.BitsAllocated
    ds.HighBit = ds.BitsStored - 1
    ds.PixelRepresentation = 0
    if fotometria == "RGB":
        ds.PlanarConfiguration = 0
    if cortes:
        ds.NumberOfFrames = cortes
    ds.PixelData = pixeles.tobytes()
    for nombre, valor in metadatos.items():
        setattr(ds, nombre, valor)
    archivo = io.BytesIO()
    ds.save_as(archivo, enforce_file_format=True)
    archivo.name = "prueba.dcm"
    return archivo


class ImagenesTests(unittest.TestCase):
    def setUp(self):
        self.grises = np.array([[0, 50, 100], [150, 200, 250]], dtype=np.uint16)

    def test_png(self):
        archivo = io.BytesIO()
        Image.new("RGB", (8, 8), (12, 34, 56)).save(archivo, format="PNG")
        archivo.name = "prueba.png"
        self.assertEqual(cargar_imagen(archivo).getpixel((0, 0)), (12, 34, 56))

    def test_monochrome1_invierte_grises(self):
        normal = np.asarray(cargar_imagen(dicom(self.grises)))
        invertida = np.asarray(cargar_imagen(dicom(self.grises, "MONOCHROME1")))
        np.testing.assert_array_equal(invertida, 255 - normal)

    def test_multiframe_de_tres_columnas_elige_centro(self):
        volumen = np.stack([self.grises[::-1], self.grises, self.grises[:, ::-1]])
        central = cargar_imagen(dicom(volumen, cortes=3))
        np.testing.assert_array_equal(np.asarray(central), np.asarray(cargar_imagen(dicom(self.grises))))

    def test_ventana_recorta_extremos(self):
        imagen = np.asarray(cargar_imagen(dicom(
            self.grises, RescaleSlope=2, RescaleIntercept=-100, WindowCenter=100, WindowWidth=200)))
        self.assertTrue(np.all(imagen[0, :2] == 0))
        self.assertTrue(np.all(imagen[1, :] == 255))

    def test_rgb_conserva_colores(self):
        colores = np.array([[[10, 20, 30], [40, 50, 60]]], dtype=np.uint8)
        np.testing.assert_array_equal(np.asarray(cargar_imagen(dicom(colores, "RGB"))), colores)

    def test_uniforme_y_fotometria_no_soportada(self):
        for archivo in (dicom(np.zeros((2, 3), dtype=np.uint16)), dicom(self.grises, "PALETTE COLOR")):
            with self.assertRaises(ValueError):
                cargar_imagen(archivo)
