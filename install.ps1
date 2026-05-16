# GraphStack v4 Installer — thin PowerShell shim that delegates to the Python core.
# Real logic lives in scripts/graphstack/installer.py.
#
# Usage: .\install.ps1 [target] [-y|--non-interactive]

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$packageParent = Join-Path $scriptDir 'scripts'
$env:PYTHONPATH = if ($env:PYTHONPATH) {
    "$packageParent;$env:PYTHONPATH"
} else {
    $packageParent
}

function Resolve-Python {
    # On Windows, prefer `py -3` because `python.exe` is often the Microsoft
    # Store redirect stub which prints a localized error and exits 9009.
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
    Write-Error 'GraphStack: Python 3.8+ is required but was not found on PATH.'
    exit 127
}

& $python.Exe @($python.PreArgs) -m graphstack install @args
exit $LASTEXITCODE
