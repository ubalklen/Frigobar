param(
    [Parameter(Mandatory=$true)]
    [string]$PythonVersion,
    [Parameter()]
    [string]$TargetDirectory=(Get-Location).Path,
    [Parameter()]
    [switch]$MoveFiles,
    [Parameter()]
    [string]$PythonDirectory
)

if ($MoveFiles){
    if (Test-Path "$PythonDirectory/Lib/site-packages/tkinter") {
        Write-Host "Tkinter already downloaded"
        exit 0
    }
}

Write-Host "Downloading the source of Python $PythonVersion to get Tkinter"
$PythonBaseUrl = "https://www.python.org/ftp/python"
$PythonSourceFilename = "Python-$PythonVersion.tgz"
$PythonSourceUrl = "$PythonBaseUrl/$PythonVersion/$PythonSourceFilename"
$PythonSourcePath = Join-Path $TargetDirectory $PythonSourceFilename
$Proxy = [System.Net.WebRequest]::GetSystemWebproxy()
$ProxyBypassed = $Proxy.IsBypassed($PythonSourceUrl)
try {
    if ($ProxyBypassed){
        Invoke-WebRequest -Uri $PythonSourceUrl -OutFile $PythonSourcePath
    } else {
        $ProxyUrl = $Proxy.GetProxy($PythonSourceUrl)
        Invoke-WebRequest -Uri $PythonSourceUrl -OutFile $PythonSourcePath -Proxy $ProxyUrl -ProxyUseDefaultCredentials
    }
}
catch {
    Write-Host "Failed to download the Python source: $_"
    Exit 1
}

Write-Host "Extracting tkinter"
$TkinterPath = "Python-$PythonVersion/Lib/tkinter"
try {
    tar -C $TargetDirectory --strip-components 2 -xf $PythonSourcePath $TkinterPath
}
catch {
    Write-Host "Failed to extract the inner tar file: $_"
    Exit 1
}

Write-Host "Downloading Tcl/Tk"
$TclTkZipFilename = "irontcl-amd64-8.6.7.zip"
$TclTkUrl = "https://www.irontcl.com/downloads/$TclTkZipFilename"
$TclTkZipPath = Join-Path $TargetDirectory $TclTkZipFilename
$ProxyBypassed = $Proxy.IsBypassed($PythonSourceUrl)
try {
    if ($ProxyBypassed){
        Invoke-WebRequest -Uri $TclTkUrl -OutFile $TclTkZipPath
    } else {
        $ProxyUrl = $Proxy.GetProxy($TclTkUrl)
        Invoke-WebRequest -Uri $TclTkUrl -OutFile $TclTkZipPath -Proxy $ProxyUrl -ProxyUseDefaultCredentials
    }	
}
catch {
    Write-Host "Failed to download the Tcl/Tk archive: $_"
    Exit 1
}

Write-Host "Extracting relevant Tcl/Tk DLLs and libs"
$TclTkBinPath = "IronTcl/bin"
$TclDllPath = "$TclTkBinPath/tcl86t.dll"
$TkDllPath = "$TclTkBinPath/tk86t.dll"
$TclTkLibPath = "IronTcl/lib"
$TclLibPath = "$TclTkLibPath/tcl8.6"
$TkLibPath = "$TclTkLibPath/tk8.6"

try {
    tar -C $TargetDirectory --strip-components 2 -xf $TclTkZipPath $TclDllPath
    tar -C $TargetDirectory --strip-components 2 -xf $TclTkZipPath $TkDllPath
    tar -C $TargetDirectory --strip-components 2 -xf $TclTkZipPath $TclLibPath
    tar -C $TargetDirectory --strip-components 2 -xf $TclTkZipPath $TkLibPath
}
catch {
    Write-Host "Failed to extract relevant Tcl/Tk DLLs and libs: $_"
    Exit 1
}

Write-Host "Cleaning up"
Remove-Item $PythonSourcePath
Remove-Item $TclTkZipPath

if ($MoveFiles) {
    Write-Host "Moving files into Python directory"
    Move-Item "$TargetDirectory/tkinter" "$PythonDirectory/Lib/site-packages"
    Move-Item "$TargetDirectory/tcl86t.dll" $PythonDirectory
    Move-Item "$TargetDirectory/tk86t.dll" $PythonDirectory

    $LibDirectory = Join-Path $PythonDirectory "..\lib"
    if (-not (Test-Path $LibDirectory)) {
        New-Item -ItemType Directory -Path $LibDirectory
    }

    Move-Item "$TargetDirectory/tcl8.6" $LibDirectory
    Move-Item "$TargetDirectory/tk8.6" $LibDirectory

    $TkinterPydPath = Join-Path $TargetDirectory "_tkinter.pyd"
    Move-Item $TkinterPydPath "$PythonDirectory"
}