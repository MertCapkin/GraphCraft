# GraphStack — Smart Graph Update Hook (thin PowerShell shim).
# Real logic lives in scripts/graphstack/hook.py.

$ErrorActionPreference = 'Stop'

try {
    $repoRoot = (& git rev-parse --show-toplevel 2>$null).Trim()
    if (-not $repoRoot) { $repoRoot = (Get-Location).Path }
} catch {
    $repoRoot = (Get-Location).Path
}

$packageParent = Join-Path $repoRoot 'scripts'
$env:PYTHONPATH = if ($env:PYTHONPATH) {
    "$packageParent;$env:PYTHONPATH"
} else {
    $packageParent
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

$python = Resolve-Python
if (-not $python) {
    Write-Host 'GraphStack: Python not found - skipping graph update.'
    exit 0
}

Push-Location $repoRoot
try {
    & $python.Exe @($python.PreArgs) -m graphstack hook
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
