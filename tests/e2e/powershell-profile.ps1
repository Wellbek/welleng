# Exercises home/Documents/PowerShell/welleng.ps1 with stub tools. Needs PowerShell 7 on Linux or macOS,
# because the stubs are shell scripts. Writes only under $HOME/.config/welleng and the temp directory,
# so run it in a container or CI: pwsh -NoProfile -File tests/e2e/powershell-profile.ps1
$ErrorActionPreference = 'Stop'
if ($env:WELLENG_E2E_CONTAINER -ne '1' -and $env:CI -ne 'true') {
  throw 'refusing to write under $HOME outside a container or CI, set WELLENG_E2E_CONTAINER=1 to override'
}
$profilePath = Join-Path $PSScriptRoot '../../home/Documents/PowerShell/welleng.ps1'
# 1. no tools at all: must not throw and must define nothing
. $profilePath
if (Get-Command y -ErrorAction SilentlyContinue) { throw 'y defined without yazi' }
'ok  loads with no tools installed'
# 2. stubs
$bin = Join-Path ([IO.Path]::GetTempPath()) 'stubs'; New-Item -ItemType Directory -Force $bin | Out-Null
$target = Join-Path ([IO.Path]::GetTempPath()) 'target'; New-Item -ItemType Directory -Force $target | Out-Null
Set-Content -Path "$bin/yazi" -Value "#!/bin/sh`nfor a in `"`$@`"; do case `"`$a`" in --cwd-file=*) printf '%s' '$target' > `"`${a#--cwd-file=}`";; esac; done"
Set-Content -Path "$bin/lazygit" -Value "#!/bin/sh"
chmod +x "$bin/yazi" "$bin/lazygit"
$env:PATH = "$bin$([IO.Path]::PathSeparator)$env:PATH"
New-Item -ItemType Directory -Force "$HOME/.config/welleng" | Out-Null
Set-Content "$HOME/.config/welleng/lazygit.yml" 'x: 1'
. $profilePath
if (-not (Get-Command y -ErrorAction SilentlyContinue)) { throw 'y missing' }
if (-not $env:LG_CONFIG_FILE) { throw 'LG_CONFIG_FILE not set' }
'ok  lazygit config set, y defined'
Set-Location /
y
if ($PWD.Path -ne $target) { throw "y did not change directory: $($PWD.Path)" }
'ok  y changes directory'
