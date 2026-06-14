param(
    [string]$Destination = "$HOME\.codex\skills"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $repoRoot "skills"

function Assert-PathUnderRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $rootPath = [System.IO.Path]::GetFullPath($Root).TrimEnd('\', '/')
    $rootPrefix = $rootPath + [System.IO.Path]::DirectorySeparatorChar

    if (-not ($fullPath.Equals($rootPath, [System.StringComparison]::OrdinalIgnoreCase) -or $fullPath.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase))) {
        throw "Refusing to modify outside destination: $fullPath"
    }
}

if (-not (Test-Path -LiteralPath $source)) {
    throw "Missing skills directory: $source"
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null
$destinationRoot = (Resolve-Path -LiteralPath $Destination).Path

Get-ChildItem -LiteralPath $source -Directory | ForEach-Object {
    $target = Join-Path $destinationRoot $_.Name
    if (Test-Path -LiteralPath $target) {
        $targetPath = (Resolve-Path -LiteralPath $target).Path
        Assert-PathUnderRoot -Path $targetPath -Root $destinationRoot
        Remove-Item -LiteralPath $targetPath -Recurse -Force
    }
    Copy-Item -LiteralPath $_.FullName -Destination $destinationRoot -Recurse -Force
    Write-Host "Installed $($_.Name) -> $target"
}
