-- Managed by chezmoi on Windows only, see .chezmoiignore. Edit it in the welleng repository.
-- WezTerm is only the skin (ADR 0003). Best effort on native Windows (ADR 0004), not verified.
-- To start in a WSL2 tmux session, set WELLENG_WSL_DISTRO to the distribution name, for example
-- with: setx WELLENG_WSL_DISTRO Ubuntu-24.04
local wezterm = require("wezterm")
local config = wezterm.config_builder()

config.scrollback_lines = 20000
config.audible_bell = "Disabled"
config.window_padding = { left = 4, right = 4, top = 4, bottom = 4 }
config.window_close_confirmation = "NeverPrompt"
config.hide_tab_bar_if_only_one_tab = true

-- The tmux prefix is M-o, so a left Alt press must reach the program as Alt, not as a composed key.
config.send_composed_key_when_left_alt_is_pressed = false
config.send_composed_key_when_right_alt_is_pressed = false

local distro = os.getenv("WELLENG_WSL_DISTRO")
if distro and distro ~= "" then
  config.default_prog = { "wsl.exe", "-d", distro, "--cd", "~", "--", "tmux", "new", "-A", "-s", "welleng" }
else
  config.default_prog = { "pwsh.exe", "-NoLogo" }
end

return config
