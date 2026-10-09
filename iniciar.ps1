# Inicia Streamlit desde la carpeta del proyecto para cargar .streamlit/config.toml.
Push-Location -LiteralPath $PSScriptRoot
try {
    & "$PSScriptRoot\.venv\Scripts\python.exe" -m streamlit run "$PSScriptRoot\app.py"
} finally {
    Pop-Location
}
