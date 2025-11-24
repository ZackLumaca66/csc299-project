<#
PowerShell launcher for Task-Neko.
Usage examples:
  ./run.ps1
  ./run.ps1 -DataFile task-neko\mydata.json
  ./run.ps1 -TestActions '[{"action":"add","text":"hi"}]'
  ./run.ps1 -DefaultLife 40
#>
param(
    [string]$TestActions = "",
    [string]$DataFile = "",
    [switch]$Dev,
    [int]$DefaultLife = 50
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

# Activate venv if present
$activate = Join-Path $PWD ".venv\Scripts\Activate.ps1"
if (Test-Path $activate) {
    Write-Host "Activating venv..."
    & $activate
}

if ($TestActions -ne "") { $env:TASK_NEKO_TEST_ACTIONS = $TestActions }
if ($DataFile -ne "") { $env:TASK_NEKO_DATA_FILE = $DataFile }
if ($DefaultLife -ne 50) { $env:TASK_NEKO_DEFAULT_LIFE = $DefaultLife.ToString() }

# Ensure TERM/COLORTERM for richer output (PowerShell/Windows Terminal usually fine)
if (-not $env:TERM) { $env:TERM = "xterm-256color" }
if (-not $env:COLORTERM) { $env:COLORTERM = "truecolor" }

$py = Join-Path $PWD ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "Running Task-Neko..."
& $py "task-neko\main.py"
