param(
	[switch]$PreferPython
)

$ErrorActionPreference = 'Stop'

function Write-Section([string]$title) {
	Write-Host ""
	Write-Host "== $title ==" -ForegroundColor Cyan
}

function Test-Command([string]$name) {
	$cmd = Get-Command $name -ErrorAction SilentlyContinue
	return $null -ne $cmd
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Section 'FC Tycoon Translations Validator'
Write-Host "Folder: $root"

$hasNode = Test-Command 'node'
$hasNpm = Test-Command 'npm'
$hasPython = Test-Command 'python'

if (-not $hasNode -or -not $hasNpm) {
	Write-Host 'Node.js is required for the default validator.' -ForegroundColor Yellow
	Write-Host 'Install Node.js LTS from: https://nodejs.org/'
	Write-Host ''
	Write-Host 'After installing Node.js:'
	Write-Host '  1) Open this folder in a terminal'
	Write-Host '  2) Run: npm install'
	Write-Host '  3) Run: npm run validate'
	if (-not $hasPython) {
		exit 1
	}
}

if ($PreferPython -and $hasPython) {
	Write-Section 'Python validator'
	if (-not (Test-Path '.\requirements.txt')) {
		Write-Host 'requirements.txt not found.' -ForegroundColor Red
		exit 1
	}
	python -m pip --version | Out-Null
	python -m pip install -r requirements.txt
	python validate-yaml.py
	exit $LASTEXITCODE
}

Write-Section 'Node validator'
if (-not (Test-Path '.\package.json')) {
	Write-Host 'package.json not found.' -ForegroundColor Red
	exit 1
}

if (-not (Test-Path '.\node_modules')) {
	Write-Host 'Installing dependencies...' -ForegroundColor Gray
	npm install
}

npm run validate
exit $LASTEXITCODE
