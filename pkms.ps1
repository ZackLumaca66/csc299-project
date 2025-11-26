#!/usr/bin/env pwsh
# PKMS launcher for PowerShell
param([Parameter(ValueFromRemainingArguments=$true)]$Args)
# Prefer repo .venv python if available
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoPython = Join-Path $repo '.venv\Scripts\python.exe'
if (Test-Path $repoPython) {
    if ($Args) { & $repoPython -m pkms_core.cli @Args } else { & $repoPython -m pkms_core.cli }
} else {
    if ($Args) { python -m pkms_core.cli @Args } else { python -m pkms_core.cli }
}
