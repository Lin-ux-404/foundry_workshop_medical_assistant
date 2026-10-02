param(
    [string]$EnvFile,
    [string]$ModelDeployment = 'gpt-5.4-nano'
)
# Only the backend reads the configuration file. This script passes its path.
if ($EnvFile) { $env:MEDICAL_ASSISTANT_ENV_FILE = $EnvFile }
$env:AZURE_AI_MODEL_DEPLOYMENT_NAME = $ModelDeployment
Push-Location (Join-Path $PSScriptRoot 'backend')
try {
    & .venv/Scripts/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
} finally {
    Pop-Location
}
