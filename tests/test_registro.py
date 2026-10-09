import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import registro_datos as registro


class RegistroTests(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.ruta = Path(self.temporal.name) / "datos" / "registro.csv"
        parche = patch.object(registro, "RUTA_CSV", self.ruta)
        parche.start()
        self.addCleanup(parche.stop)

    def test_creacion_y_analisis_repetidos(self):
        self.assertEqual(registro.obtener_resultados(), [])
        for _ in range(2):
            registro.guardar_resultado("Paciente prueba", "001", "CNN", "Sin tumor", 0.987654321,
                                       "imagen.png", huella_imagen="a" * 64, version_modelo="b" * 64)
        filas = registro.obtener_resultados()
        self.assertEqual(len(filas), 2)
        self.assertNotEqual(filas[0]["id_analisis"], filas[1]["id_analisis"])
        self.assertEqual(filas[0]["confianza"], 0.987654321)
        self.assertEqual(filas[0]["version_modelo"], "b" * 64)

    def test_formato_antiguo_migracion_y_respaldo(self):
        self.ruta.parent.mkdir()
        with self.ruta.open("w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(registro.COLUMNAS_ANTERIORES)
            escritor.writerow(["2026-10-09", "Anterior", "001", "CNN", "Sin tumor", "95.2%", "a.png"])
        anterior = self.ruta.read_bytes()
        self.assertAlmostEqual(registro.obtener_resultados()[0]["confianza"], 0.952)
        self.assertEqual(self.ruta.read_bytes(), anterior)
        registro.guardar_resultado("Nuevo", "002", "CNN", "Sin tumor", 0.9)
        respaldo, = self.ruta.parent.glob("*.respaldo-*.csv")
        self.assertEqual(respaldo.read_bytes(), anterior)
        filas = registro.obtener_resultados()
        self.assertEqual(len(filas), 2)
        self.assertTrue(filas[0]["id_analisis"])
        self.assertEqual(filas[0]["huella_imagen"], "")
        registro.guardar_resultado("Nuevo", "002", "CNN", "Sin tumor", 0.9)
        self.assertEqual(len(list(self.ruta.parent.glob("*.respaldo-*.csv"))), 1)

    def test_csv_invalido_no_se_modifica(self):
        self.ruta.parent.mkdir()
        casos = [b"", b"columnas,incorrectas\n", b"\xff\xfe",
                 (",".join(registro.COLUMNAS) + "\nsolo,dos\n").encode()]
        for contenido in casos:
            with self.subTest(contenido=contenido):
                self.ruta.write_bytes(contenido)
                with self.assertRaises(registro.ErrorRegistro):
                    registro.obtener_resultados()
                self.assertEqual(self.ruta.read_bytes(), contenido)

    def test_confianza_invalida_no_crea_archivo(self):
        for valor in ("nan", "inf", -0.1, 1.1, "110%", "texto"):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                registro.guardar_resultado("Prueba", "1", "CNN", "Sin tumor", valor)
        self.assertFalse(self.ruta.exists())

    def test_error_de_permisos(self):
        with patch("builtins.open", side_effect=PermissionError):
            with self.assertRaises(registro.ErrorRegistro):
                registro.obtener_resultados()
