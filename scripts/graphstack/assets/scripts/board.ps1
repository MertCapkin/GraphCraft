# GraphStack GNAP board — thin PowerShell shim that delegates to the Python core.
# Real logic lives in scripts/graphstack/board.py.
#
# Usage: .\scripts\board.ps1 <command> [args]

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = if ($env:PYTHONPATH) {
    "$scriptDir;$env:PYTHONPATH"
} else {
    $scriptDir
}

function Resolve-Python {
    # On Windows, prefer `py -3` because `python.exe` is often the Microsoft
    # Store redirect stub which prints a localized error and exits 9009.
    $py = Get-Command 'py' -ErrorAction SilentlyContinue
    if ($py) { return [pscustomobject]@{ Exe = $py.Source; PreArgs = @('-3') } }
    foreach ($name in @('python3', 'python')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        # Skip the Windows Store stub (lives under WindowsApps).
        if ($cmd.Source -match 'WindowsApps') { continue }
        return [pscustomobject]@{ Exe = $cmd.Source; PreArgs = @() }
    }
    return $null
}

$python = Resolve-Python
if (-not $python) {
    Write-Error 'GraphStack: Python not found. Install Python 3.8+ and retry.'
    exit 127
}

& $python.Exe @($python.PreArgs) -m graphstack board @args
exit $LASTEXITCODE
