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
