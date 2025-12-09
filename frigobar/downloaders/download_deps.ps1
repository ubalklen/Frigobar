# A script to download and install dependencies listed in a requirements file from pip
# Usage: .\download_deps.ps1 [-RequirementsFile <RequirementsFile>] [-PythonPath <PythonPath>]
# Example: .\download_deps.ps1 requirements.txt python\install\python.exe

param(
    [Parameter()]
    [string]$RequirementsFile="requirements.txt",
    [Parameter()]
    [string]$PythonPath="python\python.exe"
)

& $PythonPath -m pip install -r $RequirementsFile --no-warn-script-location
Write-Host "Done"
