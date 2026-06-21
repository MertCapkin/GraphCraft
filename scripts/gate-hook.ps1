# GraphCraft + GraphStack process gate — Cursor hooks shim.
# Design gate (GraphCraft) runs first when .graphcraft-framework exists.

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

$env:PYTHONPATH = if ($env:PYTHONPATH) {
    "$scriptDir;$env:PYTHONPATH"
} else {
    $scriptDir
}

function Resolve-Python {
    $py = Get-Command 'py' -ErrorAction SilentlyContinue
    if ($py) { return [pscustomobject]@{ Exe = $py.Source; PreArgs = @('-3') } }
    foreach ($name in @('python3', 'python')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        if ($cmd.Source -match 'WindowsApps') { continue }
        return [pscustomobject]@{ Exe = $cmd.Source; PreArgs = @() }
    }
    return $null
}

$platform = if ($args.Count -gt 0) { $args[0] } else { 'cursor' }

$python = Resolve-Python
if (-not $python) {
    Write-Host 'gate-hook: Python not found — failing open' -ForegroundColor Yellow
    if ($platform -eq 'cursor') {
        Write-Output '{"continue": true, "permission": "allow"}'
    } else {
        Write-Output '{}'
    }
    exit 0
}

$stdinText = [Console]::In.ReadToEnd()

$isGraphCraft = Test-Path (Join-Path $repoRoot '.graphcraft-framework')

if ($isGraphCraft) {
    Push-Location $repoRoot
    try {
        $stdinText | & $python.Exe @($python.PreArgs) -m graphcraft gate hook @args
        if ($LASTEXITCODE -eq 2) {
            exit 0
        }
    } finally {
        Pop-Location
    }
}

Push-Location $repoRoot
try {
    $stdinText | & $python.Exe @($python.PreArgs) -m graphstack gate hook @args
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
