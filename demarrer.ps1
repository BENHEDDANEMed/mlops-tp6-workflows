param(
    [ValidateSet('serveur', 'workflow', 'serve', 'pool', 'worker', 'qualite')]
    [string]$Role = 'workflow'
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$env:PATH = (Join-Path $PSScriptRoot '.venv\Scripts') + ';' + $env:PATH
$env:PREFECT_HOME = Join-Path $PSScriptRoot '.prefect'
$env:PREFECT_API_URL = 'http://127.0.0.1:4200/api'
$env:PREFECT_SERVER_ANALYTICS_ENABLED = 'false'
$env:PYTHONIOENCODING = 'utf-8'
$PythonTP6 = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
switch ($Role) {
    'serveur'  { & $PythonTP6 -m prefect server start --host 127.0.0.1 }
    'workflow' { & $PythonTP6 flow_mlops.py }
    'serve'    { & $PythonTP6 planifier.py }
    'pool' {
        & $PythonTP6 -m prefect work-pool inspect pool-tp *> $null
        if ($LASTEXITCODE -ne 0) {
            & $PythonTP6 -m prefect work-pool create pool-tp --type process
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        }
        & $PythonTP6 -m prefect deploy --name hebdomadaire-pool --no-prompt
    }
    'worker' { & $PythonTP6 -m prefect worker start --pool pool-tp --limit 1 }
    'qualite' { & $PythonTP6 verifier_qualite.py }
}
exit $LASTEXITCODE
