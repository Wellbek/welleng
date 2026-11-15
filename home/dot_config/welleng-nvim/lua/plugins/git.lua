-- Git workflow keys. LazyVim already provides gitsigns with the <leader>gh hunk keys and [h ]h,
-- so this only adds diffview for whole-repository and per-file history review, and two extras.
return {
  {
    "sindrets/diffview.nvim",
    cmd = { "DiffviewOpen", "DiffviewClose", "DiffviewFileHistory", "DiffviewToggleFiles" },
    opts = { enhanced_diff_hl = true },
    keys = {
      { "<leader>gd", "<cmd>DiffviewOpen<cr>", desc = "Diffview: working tree" },
      { "<leader>gm", "<cmd>DiffviewOpen origin/HEAD...HEAD<cr>", desc = "Diffview: branch against origin" },
      { "<leader>gH", "<cmd>DiffviewFileHistory %<cr>", desc = "Diffview: history of this file" },
      { "<leader>gq", "<cmd>DiffviewClose<cr>", desc = "Diffview: close" },
    },
  },
  {
    "lewis6991/gitsigns.nvim",
    keys = {
      { "<leader>gT", "<cmd>Gitsigns toggle_current_line_blame<cr>", desc = "Toggle line blame" },
    },
  },
}
