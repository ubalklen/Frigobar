# A script to download Python from python-build-standalone
# Usage: .\download_python.ps1 [-Version <Version>] [-Timestamp <Timestamp>] [-Configuration <Configuration>] [-Flavor <Flavor>] [-TargetDirectory <TargetDirectory>]
# Example: .\download_python.ps1 -Version 3.12.0
# Example: .\download_python.ps1 -Version 3.10.19 -Timestamp 20251205 -Configuration x86_64-pc-windows-msvc

param(
    [Parameter()]
    [string]$Version="3.13.11",
    [Parameter()]
    [string]$Timestamp="20251205",
    [Parameter()]
    [string]$Configuration="x86_64-pc-windows-msvc",
    [Parameter()]
    [string]$Flavor="install_only_stripped",
    [Parameter()]
    [string]$TargetDirectory=(Get-Location).Path
)

# Build the filename and URL
# Format: cpython-{version}+{timestamp}-{configuration}-{flavor}.tar.{ext}
$FileName = "cpython-$Version+$Timestamp-$Configuration-$Flavor"

# Determine file extension (install_only_stripped uses .tar.gz, others typically use .tar.zst)
if ($Flavor -eq "install_only_stripped") {
    $FileExt = "tar.gz"
} else {
    $FileExt = "tar.zst"
}

$ArchiveFile = "$FileName.$FileExt"
$ArchivePath = "$TargetDirectory\$ArchiveFile"
$PythonUrl = "https://github.com/astral-sh/python-build-standalone/releases/download/$Timestamp/$ArchiveFile"
$ExtractedDir = "$TargetDirectory\python"
$PythonExe = "$ExtractedDir\python.exe"

if (Test-Path $PythonExe) {
    Write-Host "Python $Version already downloaded"
    exit 0
}

Write-Host "Downloading Python $Version from python-build-standalone"
Write-Host "URL: $PythonUrl"

try {
    $Proxy = [System.Net.WebRequest]::GetSystemWebproxy()
    $ProxyBypassed = $Proxy.IsBypassed($PythonUrl)
    if ($ProxyBypassed){
        Invoke-WebRequest -Uri $PythonUrl -OutFile $ArchivePath -ErrorAction Stop
    } else {
        $ProxyUrl = $Proxy.GetProxy($PythonUrl)
        Invoke-WebRequest -Uri $PythonUrl -OutFile $ArchivePath -Proxy $ProxyUrl -ProxyUseDefaultCredentials -ErrorAction Stop
    }
} catch {
    Write-Host "Error when downloading $PythonUrl. Please, make sure it is listed in https://github.com/astral-sh/python-build-standalone/releases" -ForegroundColor Red
    exit 1
}

Write-Host "Extracting Python $Version"

# Extract tar.gz or tar.zst archive
# First, we need to check if tar is available (Windows 10+ has native tar support)
if (Get-Command tar -ErrorAction SilentlyContinue) {
    # Use native tar command
    tar -xf $ArchivePath -C $TargetDirectory
} else {
    Write-Host "Error: tar command not found. Please install tar or use Windows 10 or later." -ForegroundColor Red
    exit 1
}

Write-Host "Cleaning up"
Remove-Item $ArchivePath

Write-Host "Done"