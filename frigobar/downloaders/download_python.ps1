# A script to download the embeddable Python of a given version
# Also configures the embeddable Python to allow pip (it's not allowed by default)
# Usage: .\download_python.ps1 -Version <Version> [-TargetDirectory <TargetDirectory>]
# Example: .\download_python.ps1 3.8.0 -TargetDirectory C:\Python\3.8.0

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    [Parameter()]
    [string]$TargetDirectory=(Get-Location).Path
)
$PythonDirName = "python-$Version-embed-amd64"
$PythonDir = "$TargetDirectory\$PythonDirName"
$PythonUrl = "https://www.python.org/ftp/python/$Version/$PythonDirName.zip"
$PythonZip = "$TargetDirectory\$PythonDirName.zip"
$PythonExe = "$PythonDirName\python.exe"

if (Test-Path $PythonExe) {
    Write-Host "Python $version already downloaded"
    exit 0
}

Write-Host "Downloading Python $Version"
# Checking if there is a proxy
$Proxy = [System.Net.WebRequest]::GetSystemWebproxy()
$ProxyBypassed = $Proxy.IsBypassed($PythonUrl)
if ($ProxyBypassed){
    Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonZip
} else {
    $ProxyUrl = $Proxy.GetProxy($PythonUrl)
    Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonZip -Proxy $ProxyUrl -ProxyUseDefaultCredentials
}

Write-Host "Extracting Python $version"
Expand-Archive -Path $PythonZip -DestinationPath "$PythonDir"

# Modify _pht file to allow pip in embedabble Python
# See https://stackoverflow.com/a/48906746
$PthFile = Get-ChildItem -Path $PythonDir -Filter "python*_pth" | Select-Object -Last 1

if ($PthFile) {
    # Read the content of the file into an array
    $Lines = Get-Content $PthFile.FullName

    # Find the last line of the file
    $LastLineIndex = $Lines.Count - 1

    # Uncomment the last line by removing the leading '#'
    $Lines[$LastLineIndex] = $Lines[$LastLineIndex] -replace '^#', ''

    # Write the updated content back to the file
    $Lines | Set-Content $PthFile.FullName

    Write-Host "Uncommented the last line in $($file.FullName)."
} else {
    Write-Host "No file found that matches the pattern (python*_pth)."
}

Write-Host "Cleaning up"
Remove-Item $PythonZip

Write-Host "Done"