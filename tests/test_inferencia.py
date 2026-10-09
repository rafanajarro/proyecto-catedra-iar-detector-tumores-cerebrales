import unittest
import numpy as np

from src.inferencia import validar_probabilidades


class ProbabilidadesTests(unittest.TestCase):
    def test_softmax_valido_y_precision_float32(self):
        for salida in ([0, 0, 0, 1], np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)):
            np.testing.assert_allclose(validar_probabilidades(salida), salida)

    def test_salidas_invalidas(self):
        for salida in ([0.2, 0.3, 0.5], [[0.1, 0.2, 0.3, 0.4]], [np.nan, 0, 0, 1],
                       [np.inf, 0, 0, 1], [-0.1, 0.2, 0.3, 0.6], [1.1, 0, 0, 0], [0.1] * 4):
            with self.subTest(salida=salida), self.assertRaises(ValueError):
                validar_probabilidades(salida)
