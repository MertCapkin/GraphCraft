# GraphStack one-line bootstrap for Cursor terminal (Windows / PowerShell)
# Installs MertCapkin_GraphStack from PyPI (+ graphify), then initializes the project.
#
# Usage (in your project folder, Cursor terminal):
#   irm https://raw.githubusercontent.com/MertCapkin/GraphStack/master/scripts/bootstrap.ps1 | iex
#
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
$initRc = $LASTEXITCODE
if ($initRc -ne 0) {
    Write-Host ''
    Write-Host 'Bootstrap finished with errors (exit ' $initRc ').' -ForegroundColor Yellow
    Write-Host 'PyPI package may be installed, but project init or doctor failed.'
    Write-Host 'Check output above, then run:  py -3 -m graphstack doctor'
    Write-Host 'If .cursor/rules/graphstack.mdc is missing, upgrade:  pip install -U MertCapkin_GraphStack[graphify]'
}
exit $initRc
