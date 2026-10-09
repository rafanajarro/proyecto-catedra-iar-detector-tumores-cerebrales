# MRI Console

Proyecto académico en Streamlit para clasificar imágenes en glioma,
meningioma, sin tumor y tumor pituitario con CNN, ResNet50 y EfficientNetB0.

## Entorno comprobado

Windows, Python 3.12.8, TensorFlow 2.21.0 y Keras 3.15.1.
Los tres modelos se guardaron con Keras 3.13.2 y se comprobó que cargan
y ejecutan una entrada sintética en el entorno indicado. Esta comprobación
verifica compatibilidad de ejecución, no precisión de clasificación.

`requirements.txt` fija las dependencias principales.
`requirements-lock.txt` registra también las dependencias transitivas del
entorno actual. La instalación en un entorno limpio aún no se ha comprobado.

## Instalación en Windows

Para clonar el repositorio con los modelos, instalar Git y Git LFS y ejecutar:

```powershell
git lfs install
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
git lfs pull
```

Desde la carpeta del proyecto, con Python 3.12 instalado:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Editar `.streamlit/secrets.toml` para establecer el usuario y contraseña.

Los archivos `modelo_cnn.keras`, `modelo_resnet.keras` y
`modelo_efficientnet.keras` deben estar en `modelos/`.
Los notebooks de entrenamiento pueden requerir dependencias adicionales
y acceso a sus datasets; no se incluyen en el entorno de la aplicación.

### Datos ficticios de ejemplo

El registro local y sus respaldos no se suben al repositorio. Se incluye
`datos/registro_pacientes.ejemplo.csv` con pacientes ficticios para capturas
y demostraciones. En una instalación nueva, para usar estos datos:

```powershell
Copy-Item datos/registro_pacientes.ejemplo.csv datos/registro_pacientes.csv
```

Este comando reemplaza el registro si ya existe. Sin copiar el ejemplo,
la aplicación crea un registro vacío. Las predicciones, imágenes y referencias
de modelo del ejemplo son ficticias y no provienen de inferencias reales.

### Archivos grandes

Los modelos se versionan con Git LFS mediante `.gitattributes`.
Instalar y activar Git LFS antes de agregarlos al primer commit.
La descarga del repositorio como ZIP puede no incluir los modelos completos;
se recomienda clonar y ejecutar `git lfs pull`.

## Ejecución

```powershell
.\iniciar.ps1
```

También se puede ejecutar desde la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit busca `.streamlit/config.toml` desde la carpeta de ejecución.
El iniciador establece esa carpeta automáticamente.

## Modo de desarrollo

`MODO_DESARROLLO = True` en `src/configuracion.py` permite entrar
automáticamente al recargar o reiniciar el servidor. Cambiarlo a `False`
restablece el login con las credenciales de `.streamlit/secrets.toml`.
Los resultados y formularios de la sesión no persisten al recargar con F5.

## Apariencia y recarga

Se conserva la paleta verde y azul claro, con fuente sans serif.
El dashboard muestra métricas, distribución por clase, uso de modelos y
los cinco análisis más recientes. La confianza promedio no es una medida
de precisión del modelo.

`server.runOnSave = true` recarga la aplicación al guardar cambios,
evitando el aviso que solicita pulsar Rerun. `client.toolbarMode = "minimal"`
reduce los controles de desarrollo. Reiniciar Streamlit tras cambiar estas
opciones. Se retiraron las referencias al icono y fondo de imagen antiguos.

## Credenciales locales

El login lee la sección `[acceso]` de `.streamlit/secrets.toml` mediante
`st.secrets`. Este archivo está excluido del control de versiones.
Para una instalación nueva, copiar `.streamlit/secrets.toml.example` a
`.streamlit/secrets.toml` y completar `usuario` y `contrasena` como textos.
Iniciar desde la carpeta del proyecto o usar `iniciar.ps1`.
Reiniciar Streamlit después de crear o cambiar este archivo.

## Organización

```text
app.py                  Inicio, estado de sesión y navegación
src/configuracion.py    Rutas, constantes y modo de desarrollo
src/inferencia.py       Carga con caché, predicción y validación
src/imagenes.py         Lectura de imágenes y DICOM
src/registro_datos.py   Lectura, validación y escritura del CSV
src/estilos.py          CSS de la aplicación
src/vistas/             Login, consola, dashboard y registro
modelos/                Modelos exportados en formato Keras
datos/                  CSV y respaldos de actualización de formato
notebooks/              Análisis y entrenamiento
.streamlit/config.toml  Tema de Streamlit
```

Los módulos `configuracion.py` y `registro_datos.py` de la raíz son
puentes de compatibilidad; el código principal está en `src/`.

## Registro y modelos

Cada análisis guardado genera una fila con ID único, huella de la imagen
y huella del archivo del modelo cargado. Repetir un análisis genera otra fila.
La confianza se almacena como proporción 0-1 y se muestra como porcentaje.
Se admite la lectura de porcentajes guardados en el formato anterior.

El CSV antiguo se amplía al guardar el siguiente análisis, con respaldo
previo en `datos/`. Las huellas de registros antiguos quedan vacías.
La persistencia está pensada para uso local; no incorpora coordinación
entre varios procesos que escriban simultáneamente.

Los modelos reciben RGB de 224 × 224 con valores 0-255. El preprocesamiento
está incorporado en los modelos exportados. La carga se conserva en caché;
si se reemplaza un modelo, reiniciar el servidor antes de usarlo.

## Imágenes DICOM

Se admiten MONOCHROME1, MONOCHROME2 y RGB de 8 bits. Se aplica la escala
de modalidad y ventana/VOI disponible antes de convertir a RGB de 8 bits.
En archivos multiframe se selecciona el corte central, sin analizar el
volumen completo. Los DICOM con grupos funcionales por corte no están
soportados. Algunas compresiones pueden necesitar decodificadores adicionales.

## Comprobación manual

1. Abrir consola, dashboard y registro.
2. Analizar una imagen con cada modelo y revisar el registro guardado.
3. Cambiar imagen o paciente y comprobar que desaparece el resultado anterior.
4. Descargar el CSV y comprobar confianza numérica e identificadores.
5. Cargar un DICOM disponible y comprobar su vista previa.

Para comprobar las dependencias instaladas:

```powershell
.\.venv\Scripts\python.exe -m pip check
```

## Pruebas automatizadas

Desde la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas usan `unittest`, incluido en Python, y las herramientas de prueba
de Streamlit. Comprueban registro CSV y respaldos, imágenes DICOM sintéticas,
probabilidades y navegación/login. Usan archivos temporales y no modifican
el registro real. No cargan los modelos ni evalúan su precisión.
