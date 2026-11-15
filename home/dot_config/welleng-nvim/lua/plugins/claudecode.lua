-- Bridge to a Claude Code session running in a tmux pane (ADR 0010).
-- The plugin only starts a loopback server and a lock file, Claude runs outside Neovim.
return {
  {
    "coder/claudecode.nvim",
    opts = { terminal = { provider = "none" } },
    keys = {
      { "<leader>a", nil, desc = "AI / Claude Code" },
      { "<leader>as", "<cmd>ClaudeCodeSend<cr>", mode = "v", desc = "Send selection to Claude" },
      { "<leader>ab", "<cmd>ClaudeCodeAdd %<cr>", desc = "Add this buffer to Claude" },
      { "<leader>aa", "<cmd>ClaudeCodeDiffAccept<cr>", desc = "Accept Claude diff" },
      { "<leader>ad", "<cmd>ClaudeCodeDiffDeny<cr>", desc = "Reject Claude diff" },
    },
  },
}
