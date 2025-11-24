#!/usr/bin/env pwsh
# PKMS launcher for PowerShell
param([Parameter(ValueFromRemainingArguments=$true)]$Args)
if ($Args) {
    python -m pkms_core.cli @Args
} else {
    python -m pkms_core.cli
}
