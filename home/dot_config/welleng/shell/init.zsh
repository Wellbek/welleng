# Well-Engineering zsh integration. Opt in with one line in ~/.zshrc, at the very end:
#   [[ -r ~/.config/welleng/shell/init.zsh ]] && source ~/.config/welleng/shell/init.zsh
# Every integration is guarded, so a missing tool never breaks the shell.
# Nothing here touches existing user configuration files.
#
# By default this only defines the credential helpers and the glm function, and adds fd and bat
# aliases where Debian naming hides them. The visible changes (prompt, zoxide, fzf, lazygit pager)
# are a separate opt-in: set WELLENG_SHELL_EXTRAS=1 in ~/.zshrc before sourcing this file.

_welleng_dir="${${(%):-%x}:A:h}"

# Credential helpers and the glm function.
[[ -r "$_welleng_dir/welleng.zsh" ]] && source "$_welleng_dir/welleng.zsh"

# Tools on Debian and Ubuntu install under different executable names.
if ! (( $+commands[fd] )) && (( $+commands[fdfind] )); then alias fd=fdfind; fi
if ! (( $+commands[bat] )) && (( $+commands[batcat] )); then alias bat=batcat; fi

if [[ "${WELLENG_SHELL_EXTRAS-}" == 1 ]]; then

# Prompt, only when the user has no starship configuration of their own.
# Every integration below is skipped when the user's shell already set it up, so this file never
# overrides existing behaviour.
if (( $+commands[starship] )) && [[ -z "${STARSHIP_SHELL-}" ]]; then
  if [[ -z "${STARSHIP_CONFIG-}" && ! -e "$HOME/.config/starship.toml" ]]; then
    export STARSHIP_CONFIG="$_welleng_dir/../starship.toml"
  fi
  eval "$(starship init zsh)"
fi

if (( $+commands[zoxide] )) && ! (( $+functions[__zoxide_z] )); then
  eval "$(zoxide init zsh)"
fi

if (( $+commands[fzf] )) && ! (( $+widgets[fzf-history-widget] )); then
  source <(fzf --zsh 2>/dev/null) 2>/dev/null
fi
if (( $+commands[fzf] )) && [[ -z "${FZF_DEFAULT_COMMAND-}" ]]; then
  if (( $+commands[fd] )); then
    export FZF_DEFAULT_COMMAND="fd --type f --hidden --exclude .git"
  elif (( $+commands[fdfind] )); then
    export FZF_DEFAULT_COMMAND="fdfind --type f --hidden --exclude .git"
  fi
fi

# yazi: use the welleng config only when the user has none, and add `y`, which changes directory on exit.
if (( $+commands[yazi] )); then
  if [[ -z "${YAZI_CONFIG_HOME-}" && ! -e "${XDG_CONFIG_HOME:-$HOME/.config}/yazi" ]]; then
    export YAZI_CONFIG_HOME="$_welleng_dir/../yazi"
  fi
  if ! (( $+functions[y] )) && ! (( $+aliases[y] )); then
    # `function y` and not `y()`: zsh refuses to parse `y()` when the user already has an alias y.
    function y {
      local tmp cwd
      tmp="$(mktemp -t yazi-cwd.XXXXXX)"
      command yazi "$@" --cwd-file="$tmp"
      if cwd="$(<"$tmp")" && [[ -n "$cwd" && "$cwd" != "$PWD" ]]; then
        builtin cd -- "$cwd"
      fi
      rm -f -- "$tmp"
    }
  fi
fi

# lazygit: add the welleng config (delta pager) after the user's own file, if they have one.
if (( $+commands[lazygit] )) && [[ -z "${LG_CONFIG_FILE-}" ]]; then
  _lg_user="${XDG_CONFIG_HOME:-$HOME/.config}/lazygit/config.yml"
  if [[ -r "$_lg_user" ]]; then
    export LG_CONFIG_FILE="$_lg_user,$_welleng_dir/../lazygit.yml"
  else
    export LG_CONFIG_FILE="$_welleng_dir/../lazygit.yml"
  fi
  unset _lg_user
fi

fi

unset _welleng_dir
