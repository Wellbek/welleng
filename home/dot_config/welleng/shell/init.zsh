# Well-Engineering zsh integration. Opt in with one line in ~/.zshrc, at the very end:
#   [[ -r ~/.config/welleng/shell/init.zsh ]] && source ~/.config/welleng/shell/init.zsh
# Every integration is guarded, so a missing tool never breaks the shell.
# Nothing here touches existing user configuration files.

_welleng_dir="${${(%):-%x}:A:h}"

# Credential helpers and the glm function.
[[ -r "$_welleng_dir/welleng.zsh" ]] && source "$_welleng_dir/welleng.zsh"

# Tools on Debian and Ubuntu install under different executable names.
if ! (( $+commands[fd] )) && (( $+commands[fdfind] )); then alias fd=fdfind; fi
if ! (( $+commands[bat] )) && (( $+commands[batcat] )); then alias bat=batcat; fi

# Prompt, only when the user has no starship configuration of their own.
if (( $+commands[starship] )); then
  if [[ -z "${STARSHIP_CONFIG-}" && ! -e "$HOME/.config/starship.toml" ]]; then
    export STARSHIP_CONFIG="$_welleng_dir/../starship.toml"
  fi
  eval "$(starship init zsh)"
fi

(( $+commands[zoxide] )) && eval "$(zoxide init zsh)"

if (( $+commands[fzf] )); then
  source <(fzf --zsh 2>/dev/null) 2>/dev/null
  if (( $+commands[fd] )); then
    export FZF_DEFAULT_COMMAND="fd --type f --hidden --exclude .git"
  elif (( $+commands[fdfind] )); then
    export FZF_DEFAULT_COMMAND="fdfind --type f --hidden --exclude .git"
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

unset _welleng_dir
