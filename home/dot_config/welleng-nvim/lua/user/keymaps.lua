-- Personal keymaps. Each one has a description, so which-key and `welleng keys` can list it.
local map = vim.keymap.set
map("n", "<leader>wk", function()
  vim.cmd("terminal welleng keys")
end, { desc = "welleng keymap cheatsheet" })
