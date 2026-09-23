# HumanPort

HumanPort is a local MCP server for inserting human decisions into an AI-agent loop. An LLM requests a choice or written response; a Tkinter window collects the answer and returns JSON through MCP.

## Features

- One Python program (no Rust, web server, or SQLite)
- MCP stdio tools including `human.request`
- Any number of choices supplied by the LLM
- Multi-line text input with `kind: input`
- In-memory processing with no persistence

## Run

```bash
python3 humanport.py
```

Register `mcp-server.json` with your MCP client. The GUI appears when a request is pending.

Answers use `values.decision` for choices and `values.text` for written input. Tasks are discarded when the process exits. MIT License.

## Approver mode (AIConductor)

With `HUMANPORT_MODE=approver`, MCP clients can only use `human.request`,
`human.await`, `human.get` and `human.capabilities`; `human.answer`,
`human.cancel` and `human.list` are not offered, so only the GUI can answer.
AIConductor uses this mode through `scripts/mcp/start-humanport-approver` and
shows the canonical action in the `detail` pane.
