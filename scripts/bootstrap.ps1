# GraphStack one-line bootstrap for Cursor terminal (Windows / PowerShell)
# Installs graphstack + graphify, then initializes the current project.
#
# Usage (in your project folder, Cursor terminal):
#   irm https://raw.githubusercontent.com/MertCapkin/GraphStack/master/scripts/bootstrap.ps1 | iex
#
# Or after PyPI publish:
#   irm ... | iex
$Pkg = "MertCapkin_GraphStack[graphify]"
# Same as:  py -3 -m pip install -U $Pkg ; py -3 -m graphstack init . -y

$ErrorActionPreference = 'Stop'

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
    Write-Error 'GraphStack bootstrap: Python 3.8+ required. Install from https://python.org/downloads/'
    exit 127
}

Write-Host ''
Write-Host 'GraphStack bootstrap' -ForegroundColor Cyan
Write-Host '===================='
Write-Host ''

& $python.Exe @($python.PreArgs) -m pip install --upgrade pip --quiet 2>$null

Write-Host "Step 1/2: Installing MertCapkin_GraphStack + graphify from PyPI..."
& $python.Exe @($python.PreArgs) -m pip install --upgrade $Pkg
if ($LASTEXITCODE -ne 0) {
    Write-Host 'PyPI install failed — trying GitHub source...' -ForegroundColor Yellow
    & $python.Exe @($python.PreArgs) -m pip install --upgrade "MertCapkin_GraphStack[graphify] @ git+https://github.com/MertCapkin/GraphStack.git"
    if ($LASTEXITCODE -ne 0) {
        Write-Error 'Could not install graphstack. Check network and Python pip.'
        exit 1
    }
}

Write-Host ''
Write-Host 'Step 2/2: Initializing GraphStack in this project...'
& $python.Exe @($python.PreArgs) -m graphstack init . -y --install-deps
exit $LASTEXITCODE
