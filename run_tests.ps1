<#
Run focused tests using the project's virtual environment without requiring activation.
If `.venv` does not exist the script will create it and install `pytest`.
#>
try {
    $py = Join-Path -Path $PSScriptRoot -ChildPath ".venv\Scripts\python.exe"
    if (-Not (Test-Path $py)) {
        Write-Host "Creating virtual environment .venv..."
        python -m venv .venv
    }
    Write-Host "Using python at: $py"
    & $py -m pip install --upgrade pip
    & $py -m pip install pytest
    & $py -m pytest tests -q
} catch {
    Write-Error "Error running tests: $_"
    exit 1
}
