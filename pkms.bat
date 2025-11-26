@echo off
REM PKMS launcher for Windows cmd/powershell when repo root is on PATH
REM Prefer the repo virtualenv python if present, otherwise fall back to system 'python'
set REPO_PYTHON=%~dp0\.venv\Scripts\python.exe
if exist "%REPO_PYTHON%" (
	"%REPO_PYTHON%" -m pkms_core.cli %*
) else (
	python -m pkms_core.cli %*
)
