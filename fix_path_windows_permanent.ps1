# PowerShell script to permanently add common directories to the user PATH
$commonPaths = @(
    "C:\Windows\System32",
    "C:\Windows",
    "C:\Windows\System32\Wbem",
    "C:\Windows\System32\WindowsPowerShell\v1.0\",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python3x\Scripts",
    "$env:USERPROFILE\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts"
)

# Get current user PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathList = $userPath -split ";"
$added = $false
foreach ($p in $commonPaths) {
    if ($p -and !("$p" -in $pathList) -and (Test-Path $p)) {
        $pathList += $p
        Write-Host "Added to PATH: $p"
        $added = $true
    }
}
if ($added) {
    $newPath = ($pathList -join ";")
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "PATH updated permanently for this user. You may need to restart your terminal or log out/in for changes to take effect."
} else {
    Write-Host "No new valid paths added. PATH is already set or folders do not exist."
}
