# Managed by chezmoi, edit it in the welleng repository.
# Best effort on native Windows (ADR 0004), not verified on a Windows host.
# Opt in with one line in your PowerShell 7 profile ($PROFILE):
#   if (Test-Path "$HOME\Documents\PowerShell\welleng.ps1") { . "$HOME\Documents\PowerShell\welleng.ps1" }
# Every integration is guarded, so a missing tool never breaks the shell, and nothing here
# changes an existing alias, function or prompt. Credentials are not handled here on purpose:
# the secrets file helpers (glm and friends) exist for zsh only.

# Prompt, only when no other prompt tool has already taken over.
if ((Get-Command starship -ErrorAction SilentlyContinue) -and -not $env:STARSHIP_SHELL) {
  if (-not $env:STARSHIP_CONFIG -and -not (Test-Path "$HOME/.config/starship.toml")) {
    $welleng = Join-Path $HOME '.config/welleng/starship.toml'
    if (Test-Path $welleng) { $env:STARSHIP_CONFIG = $welleng }
  }
  Invoke-Expression (& starship init powershell)
}

if ((Get-Command zoxide -ErrorAction SilentlyContinue) -and -not (Get-Command z -ErrorAction SilentlyContinue)) {
  Invoke-Expression (& { (zoxide init powershell | Out-String) })
}

# lazygit with the welleng pager config, after the user's own file if there is one.
if ((Get-Command lazygit -ErrorAction SilentlyContinue) -and -not $env:LG_CONFIG_FILE) {
  $lg = Join-Path $HOME '.config/welleng/lazygit.yml'
  if (Test-Path $lg) {
    $user = if ($env:APPDATA) { Join-Path $env:APPDATA 'lazygit\config.yml' } else { $null }
    $env:LG_CONFIG_FILE = if ($user -and (Test-Path $user)) { "$user,$lg" } else { $lg }
  }
}

# yazi: `y` changes the directory on exit.
if ((Get-Command yazi -ErrorAction SilentlyContinue) -and -not (Get-Command y -ErrorAction SilentlyContinue)) {
  function y {
    $tmp = New-TemporaryFile
    try {
      yazi @args --cwd-file="$tmp"
      $cwd = Get-Content -Path $tmp -Encoding UTF8 -ErrorAction SilentlyContinue
      if ($cwd -and $cwd -ne $PWD.Path -and (Test-Path -LiteralPath $cwd)) { Set-Location -LiteralPath $cwd }
    } finally {
      Remove-Item -Path $tmp -ErrorAction SilentlyContinue
    }
  }
}
