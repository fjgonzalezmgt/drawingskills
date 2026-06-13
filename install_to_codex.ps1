param(
    [string]$Destination = "$HOME\.codex\skills"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $repoRoot "skills"

if (-not (Test-Path -LiteralPath $source)) {
    throw "Missing skills directory: $source"
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null
$destinationRoot = (Resolve-Path -LiteralPath $Destination).Path

Get-ChildItem -LiteralPath $source -Directory | ForEach-Object {
    $target = Join-Path $Destination $_.Name
    if (Test-Path -LiteralPath $target) {
        $targetPath = (Resolve-Path -LiteralPath $target).Path
        if (-not $targetPath.StartsWith($destinationRoot)) {
            throw "Refusing to replace outside destination: $targetPath"
        }
        Remove-Item -LiteralPath $targetPath -Recurse -Force
    }
    Copy-Item -LiteralPath $_.FullName -Destination $Destination -Recurse -Force
    Write-Host "Installed $($_.Name) -> $target"
}
