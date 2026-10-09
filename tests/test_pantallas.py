import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from src import configuracion, registro_datos
from src.vistas.login import obtener_credenciales
import streamlit as st

APP = Path(__file__).resolve().parent.parent / "app.py"


class PantallasTests(unittest.TestCase):
    def test_login_y_cierre_de_sesion(self):
        with patch.object(configuracion, "MODO_DESARROLLO", False):
            app = AppTest.from_file(str(APP))
            app.secrets["acceso"] = {"usuario": "prueba", "contrasena": "clave_prueba"}
            app.run(timeout=30)
            app.text_input[0].set_value("prueba")
            app.text_input[1].set_value("incorrecta")
            app.button[0].click().run(timeout=30)
            self.assertFalse(app.session_state["autenticado"])
            self.assertTrue(app.error)
            app.text_input[1].set_value("clave_prueba")
            app.button[0].click().run(timeout=30)
            self.assertTrue(app.session_state["autenticado"])
            app.sidebar.button[0].click().run(timeout=30)
            self.assertFalse(app.session_state["autenticado"])
            self.assertFalse(app.exception)

    def test_credenciales_ausentes_o_invalidas(self):
        for secretos in ({}, {"acceso": {}}, {"acceso": {"usuario": "", "contrasena": "clave"}},
                         {"acceso": {"usuario": "prueba", "contrasena": 1234}}):
            with self.subTest(secretos=secretos), patch.object(st, "secrets", secretos):
                with self.assertRaises(ValueError):
                    obtener_credenciales()

    def test_desarrollo_navegacion_y_error_csv(self):
        with patch.object(configuracion, "MODO_DESARROLLO", True), \
             patch.object(registro_datos, "obtener_resultados", return_value=[]):
            app = AppTest.from_file(str(APP)).run(timeout=30)
            self.assertTrue(app.session_state["autenticado"])
            for nombre in ("Dashboard", "Registro de pacientes"):
                opcion = next(o for o in app.sidebar.radio[0].options if nombre in o)
                app.sidebar.radio[0].set_value(opcion).run(timeout=30)
                self.assertFalse(app.exception)
                with patch.object(registro_datos, "obtener_resultados",
                                  side_effect=registro_datos.ErrorRegistro("Error de prueba")):
                    app.run(timeout=30)
                    self.assertFalse(app.exception)
                    self.assertEqual(app.error[0].value, "Error de prueba")
