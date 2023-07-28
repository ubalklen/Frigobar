# A script to download and install dependencies listed in a requirements file from pip
# Usage: .\download_deps.ps1 [-RequirementsFile <RequirementsFile>] [-PipPath <PipPath>] [-UseProxy] <UseProxy>
# Example: .\download_deps.ps1 requirements.txt C:\Python\3.8.0\Scripts\pip.exe

param(
    [Parameter()]
    [string]$RequirementsFile="requirements.txt",
    [Parameter()]
    [string]$PipPath="Scripts\pip.exe",
    [Parameter()]
    [bool]$UseProxy=$false
)

& $PipPath install -r $RequirementsFile --no-warn-script-location
Write-Host "Done"
