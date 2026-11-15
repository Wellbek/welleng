-- Contextual prompts for the Claude Code session in a tmux pane (ADR 0010).
-- The selection or buffer travels through the claudecode.nvim bridge. The instruction is typed
-- into the Claude pane with tmux, without pressing Enter, so the user always reviews and sends it.
local M = {}

M.prompts = {
  explain = "Explain what the referenced code does and why.",
  fix = "Find and fix the bug in the referenced code. Explain the root cause first.",
  tests = "Write tests for the referenced code, following the conventions of this repository.",
  review = "Review the referenced code for correctness, security and maintainability.",
}

-- A pane runs Claude Code when its command is `claude`, or a bare version number: native installs
-- execute a versioned file, so tmux reports that name.
local function is_claude(cmd)
  return cmd:match("^claude") ~= nil or cmd:match("^%d+%.%d+") ~= nil
end

-- listing is the output of: tmux list-panes -F '#{pane_id}<TAB>#{pane_current_command}'
function M.find_pane(listing, own)
  for line in (listing or ""):gmatch("[^\n]+") do
    local id, cmd = line:match("^(%%%d+)\t(.*)$")
    if id and id ~= own and is_claude(cmd) then
      return id
    end
  end
end

local function tmux(args)
  local out = vim.fn.system(vim.list_extend({ "tmux" }, args))
  return vim.v.shell_error == 0, out
end

function M.pane()
  if vim.g.welleng_claude_pane then
    return vim.g.welleng_claude_pane
  end
  local own = vim.env.TMUX_PANE
  if not own then
    return nil
  end
  local ok, out = tmux({ "list-panes", "-F", "#{pane_id}\t#{pane_current_command}" })
  return ok and M.find_pane(out, own) or nil
end

function M.ask(kind, visual)
  local text = M.prompts[kind]
  vim.cmd(visual and "ClaudeCodeSend" or "ClaudeCodeAdd %")
  local pane = M.pane()
  if not pane then
    vim.fn.setreg("+", text)
    vim.notify("No Claude pane found, the prompt is on the clipboard: " .. text, vim.log.levels.WARN)
    return
  end
  tmux({ "send-keys", "-t", pane, "-l", text })
  tmux({ "select-pane", "-t", pane })
end

function M.setup()
  local map = vim.keymap.set
  for key, kind in pairs({ e = "explain", f = "fix", t = "tests", r = "review" }) do
    map("n", "<leader>a" .. key, function() M.ask(kind, false) end, { desc = "Claude: " .. kind .. " this buffer" })
    map("v", "<leader>a" .. key, function() M.ask(kind, true) end, { desc = "Claude: " .. kind .. " selection" })
  end
end

return M
