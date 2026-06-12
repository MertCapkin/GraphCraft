# GraphStack process gate — thin PowerShell shim for Cursor / Claude Code hooks.
# Real logic lives in scripts/graphstack/gate.py.
#
# Usage: .\scripts\gate-hook.ps1 <cursor|claude>

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

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
    Write-Host 'graphstack gate-hook: Python not found — failing open' -ForegroundColor Yellow
    if ($platform -eq 'cursor') {
        Write-Output '{"continue": true, "permission": "allow"}'
    } else {
        Write-Output '{}'
    }
    exit 0
}

& $python.Exe @($python.PreArgs) -m graphstack gate hook @args
exit $LASTEXITCODE
