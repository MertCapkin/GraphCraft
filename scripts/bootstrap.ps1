# GraphStack one-line bootstrap for Cursor terminal (Windows / PowerShell)
# Installs MertCapkin_GraphStack from PyPI (+ graphify), then initializes the project.
#
# Usage (in your project folder, Cursor terminal):
#   irm https://raw.githubusercontent.com/MertCapkin/GraphStack/master/scripts/bootstrap.ps1 | iex
#
$Pkg = 'MertCapkin_GraphStack[graphify]'
$GitSpec = 'MertCapkin_GraphStack[graphify] @ git+https://github.com/MertCapkin/GraphStack.git'

# Do not use Stop — pip/graphify write to stderr and Cursor marks the terminal failed.
$ErrorActionPreference = 'Continue'

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

function Invoke-GraphstackPython {
    param([string[]]$CodeArgs)
    & $python.Exe @($python.PreArgs) @CodeArgs
    return $LASTEXITCODE
}

function Test-WheelAssets {
    $rc = Invoke-GraphstackPython @(
        '-c',
        "from graphstack.installer import install_source_root; p=install_source_root()/'.cursor'/'rules'/'graphstack.mdc'; import sys; sys.exit(0 if p.is_file() else 1)"
    )
    return $rc -eq 0
}

function Install-GraphstackPackage {
    Write-Host "Step 1/2: Installing MertCapkin_GraphStack + graphify from PyPI..."
    $rc = Invoke-GraphstackPython @('-m', 'pip', 'install', '--upgrade', '--force-reinstall', $Pkg)
    if ($rc -ne 0) {
        Write-Host 'PyPI install failed — trying GitHub source...' -ForegroundColor Yellow
        $rc = Invoke-GraphstackPython @('-m', 'pip', 'install', '--upgrade', '--force-reinstall', $GitSpec)
        if ($rc -ne 0) {
            Write-Error 'Could not install graphstack. Check network and Python pip.'
            exit 1
        }
    }
    if (-not (Test-WheelAssets)) {
        Write-Host 'PyPI wheel missing .cursor assets — installing from GitHub...' -ForegroundColor Yellow
        $rc = Invoke-GraphstackPython @('-m', 'pip', 'install', '--upgrade', '--force-reinstall', $GitSpec)
        if ($rc -ne 0 -or -not (Test-WheelAssets)) {
            Write-Error 'Installed package is missing Cursor workflow files. Open an issue on GitHub.'
            exit 1
        }
    }
    $ver = (& $python.Exe @($python.PreArgs) -m graphstack --version 2>$null)
    Write-Host "  Installed: $ver"
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

$null = Invoke-GraphstackPython @('-m', 'pip', 'install', '--upgrade', 'pip', '--quiet')

Install-GraphstackPackage

Write-Host ''
Write-Host 'Step 2/2: Initializing GraphStack in this project...'
$initRc = Invoke-GraphstackPython @('-m', 'graphstack', 'init', '.', '-y', '--install-deps')

$ruleFile = Join-Path (Get-Location) '.cursor\rules\graphstack.mdc'
if (-not (Test-Path -LiteralPath $ruleFile)) {
    Write-Host ''
    Write-Host 'Bootstrap failed: .cursor/rules/graphstack.mdc was not created.' -ForegroundColor Red
    Write-Host 'Run:  py -3 -m pip install -U --force-reinstall ''MertCapkin_GraphStack[graphify]'''
    Write-Host 'Then: py -3 -m graphstack init . -y --install-deps'
    exit 1
}

if ($initRc -ne 0) {
    Write-Host ''
    Write-Host "Init reported issues (exit $initRc) but core files are present." -ForegroundColor Yellow
    Write-Host 'Run:  py -3 -m graphstack doctor'
    exit 0
}

Write-Host ''
Write-Host 'GraphStack bootstrap complete.' -ForegroundColor Green
exit 0
