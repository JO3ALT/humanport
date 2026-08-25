# HumanPort MCP Protocol

Pass `kind`, `title`, and `prompt` in `arguments.task` to `human.request`. Choice input uses `kind: "choice"` and `choices: [{"value","label"}, ...]`; written input uses `kind: "input"`.

Answers use `values.decision` for choices and `values.text` for text. Additional tools are `human.get`, `human.await`, `human.cancel`, `human.list`, and `human.capabilities`. State is in memory only.
