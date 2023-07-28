# A script to download and install pip using get-pip.py
# Usage: .\download_pip.ps1 [-TargetDirectory <TargetDirectory>] [-UseProxy <UseProxy>]
# Example: .\download_pip.ps1 -TargetDirectory C:\Python\3.8.0

param(
    [Parameter()]
    [string]$TargetDirectory=(Get-Location).Path,
    [Parameter()]
    [bool]$UseProxy=$false
)

$PipUrl = "https://bootstrap.pypa.io/get-pip.py"
$PipFile = "$TargetDirectory\get-pip.py"
$PipExe = "$TargetDirectory\Scripts\pip.exe"

if (Test-Path $PipExe) {
    Write-Host "Pip already downloaded"
    exit 0
}

Write-Host "Downloading get-pip.py"
if ($UseProxy) {
    $ProxyUrl = ([System.Net.WebRequest]::GetSystemWebproxy()).GetProxy($PipUrl)
    Invoke-WebRequest -Uri $PipUrl -OutFile $PipFile -Proxy $ProxyUrl -ProxyUseDefaultCredentials
} else {
    Invoke-WebRequest -Uri $PipUrl -OutFile $PipFile 
}

Write-Host "Installing pip"
& $TargetDirectory\python.exe $PipFile --no-warn-script-location

Write-Host "Done"