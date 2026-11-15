<#
.SYNOPSIS
  Install the tools Well-Engineering needs on native Windows, from the package map.
.DESCRIPTION
  WSL2 is the first-class Windows path (ADR 0004), run bootstrap/install.sh inside WSL2 instead.
  This script is the best-effort native fallback. It is NOT verified on a real Windows machine,
  see docs/verification/windows.md for the manual procedure.
  -DryRun shows the plan and changes nothing. Without -Yes it asks before installing.
  Packages come from winget. Tools without a winget id are reported, never installed from an
  unverified script.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File bootstrap\install.ps1 -DryRun
#>
[CmdletBinding()]
param(
  [switch]$DryRun,
  [switch]$Yes,
  [string]$Tiers = 'mandatory,recommended'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot

function Find-Python {
  foreach ($name in 'python', 'python3', 'py') {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) {
      & $cmd.Source -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>$null
      if ($LASTEXITCODE -eq 0) { return $cmd.Source }
    }
  }
  return $null
}

$python = Find-Python
if (-not $python) {
  Write-Host 'Python 3.11 or newer is required to read the package map.'
  if ($DryRun) {
    Write-Host 'dry run: would run: winget install --exact --id Python.Python.3.12'
    exit 0
  }
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    throw 'winget was not found. Install Python 3.11 or newer by hand and run this script again.'
  }
  winget install --exact --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
  Write-Host 'Python was installed. Open a new terminal so PATH updates, then run this script again.'
  exit 1
}

$lines = & $python -I (Join-Path $root 'bootstrap\plan.py') winget --tiers $Tiers
if ($LASTEXITCODE -ne 0) { throw 'could not read the package map' }

$packages = @()
foreach ($line in $lines) {
  if (-not $line) { continue }
  $kind, $name, $value = $line -split "`t", 3
  switch ($kind) {
    'pkg' { $packages += [pscustomobject]@{ Name = $name; Id = $value }; Write-Host ('package   {0,-10} {1}' -f $name, $value) }
    'fallback' { Write-Host ('manual    {0,-10} {1}' -f $name, $value) }
    default { Write-Host ('manual    {0,-10} {1}' -f $name, $value) }
  }
}

if ($packages.Count -eq 0) { Write-Host 'nothing to install via winget' }
if ($DryRun) { Write-Host 'dry run: nothing was changed'; exit 0 }
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw 'winget was not found' }

if (-not $Yes -and $packages.Count -gt 0) {
  $answer = Read-Host 'Proceed? [y/N]'
  if ($answer -ne 'y') { Write-Host 'aborted'; exit 1 }
}

$failed = @()
foreach ($p in $packages) {
  winget install --exact --id $p.Id --accept-package-agreements --accept-source-agreements
  if ($LASTEXITCODE -ne 0) { $failed += $p.Name }
}

if ($failed.Count -gt 0) {
  Write-Host ('failed: ' + ($failed -join ', '))
  exit 1
}
Write-Host 'done. Open a new terminal, then run: chezmoi init --apply --source <this repository>'
