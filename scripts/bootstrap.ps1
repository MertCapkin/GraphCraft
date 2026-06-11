# GraphStack one-line bootstrap for Cursor terminal (Windows / PowerShell)
# Installs MertCapkin_GraphStack from PyPI (+ graphify), then initializes the project.
#
# Usage (in your project folder, Cursor terminal):
#   irm https://raw.githubusercontent.com/MertCapkin/GraphStack/master/scripts/bootstrap.ps1 | iex
#
$Pkg = 'MertCapkin_GraphStack[graphify]'
$GitSpec = 'MertCapkin_GraphStack[graphify] @ git+https://github.com/MertCapkin/GraphStack.git'

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
    param(
        [string[]]$CodeArgs,
        [switch]$Quiet
    )
    if ($Quiet) {
        & $python.Exe @($python.PreArgs) @CodeArgs *>$null
    } else {
        # Out-Host prevents pip stdout from polluting the function return value ($rc = ...).
        & $python.Exe @($python.PreArgs) @CodeArgs | Out-Host
    }
    if ($null -eq $LASTEXITCODE) { return 0 }
    return [int]$LASTEXITCODE
}

function Test-WheelAssets {
    $rc = Invoke-GraphstackPython -Quiet @(
        '-c',
        "from graphstack.installer import install_source_root; p=install_source_root()/'.cursor'/'rules'/'graphstack.mdc'; import sys; sys.exit(0 if p.is_file() else 1)"
    )
    return $rc -eq 0
}

function Test-GraphstackCli {
    $rc = Invoke-GraphstackPython -Quiet @('-m', 'graphstack', '--version')
    return $rc -eq 0
}

function Install-GraphstackPackage {
    if ((Test-GraphstackCli) -and (Test-WheelAssets)) {
        $ver = (& $python.Exe @($python.PreArgs) -m graphstack --version 2>$null)
        Write-Host "Step 1/2: GraphStack already installed ($ver) - skipping pip."
        return
    }

    Write-Host 'Step 1/2: Installing MertCapkin_GraphStack + graphify from PyPI...'
    $rc = Invoke-GraphstackPython @('-m', 'pip', 'install', '--upgrade', $Pkg)
    if ($rc -ne 0) {
        Write-Host 'PyPI install failed - trying GitHub source...' -ForegroundColor Yellow
        $rc = Invoke-GraphstackPython @('-m', 'pip', 'install', '--upgrade', $GitSpec)
        if ($rc -ne 0) {
            Write-Error 'Could not install graphstack. Check network and Python pip.'
            exit 1
        }
    }

    if (-not (Test-WheelAssets)) {
        Write-Host 'PyPI wheel missing .cursor assets - reinstalling from PyPI...' -ForegroundColor Yellow
        $rc = Invoke-GraphstackPython @('-m', 'pip', 'install', '--upgrade', '--force-reinstall', $Pkg)
        if ($rc -ne 0 -or -not (Test-WheelAssets)) {
            Write-Host 'Trying GitHub source...' -ForegroundColor Yellow
            $rc = Invoke-GraphstackPython @('-m', 'pip', 'install', '--upgrade', '--force-reinstall', $GitSpec)
            if ($rc -ne 0 -or -not (Test-WheelAssets)) {
                Write-Error 'Installed package is missing Cursor workflow files. Open an issue on GitHub.'
                exit 1
            }
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

$null = Invoke-GraphstackPython -Quiet @('-m', 'pip', 'install', '--upgrade', 'pip')

$ruleFile = Join-Path (Get-Location) '.cursor\rules\graphstack.mdc'
if ((Test-GraphstackCli) -and (Test-WheelAssets) -and (Test-Path -LiteralPath $ruleFile)) {
    Write-Host 'GraphStack is already set up in this project.' -ForegroundColor Green
    Write-Host "  Rules: $ruleFile"
    Write-Host '  Health:  py -3 -m graphstack doctor'
    exit 0
}

Install-GraphstackPackage

Write-Host ''
Write-Host 'Step 2/2: Initializing GraphStack in this project...'
$initRc = Invoke-GraphstackPython @('-m', 'graphstack', 'init', '.', '-y', '--install-deps')

if (-not (Test-Path -LiteralPath $ruleFile)) {
    Write-Host ''
    Write-Host 'Bootstrap failed: .cursor/rules/graphstack.mdc was not created.' -ForegroundColor Red
    Write-Host 'Run:  py -3 -m pip install -U ''MertCapkin_GraphStack[graphify]'''
    Write-Host 'Then: py -3 -m graphstack init . -y --install-deps'
    exit 1
}

if ($initRc -ne 0) {
    Write-Host ''
    Write-Host ('Init reported issues (exit {0}) but core files are present.' -f $initRc) -ForegroundColor Yellow
    Write-Host 'Run:  py -3 -m graphstack doctor'
}

Write-Host ''
Write-Host 'GraphStack bootstrap complete.' -ForegroundColor Green
exit 0
