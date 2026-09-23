# HumanPort

HumanPort は、AIエージェントのループへ人間の判断を組み込むためのローカルMCPサーバーです。LLMが選択肢や文章入力を依頼し、Tkinterの画面で人間が回答すると、回答JSONがMCPへ返ります。

## 特徴

- Python 1本で動作（Rust、Webサーバー、SQLite不要）
- MCP stdioで `human.request` などを提供
- 選択肢の数をLLMが自由に指定
- `kind: input` で複数行の文章入力
- 回答はメモリ上で処理し、永続保存しない

## 起動

```bash
python3 humanport.py
```

MCPクライアントには `mcp-server.json` を登録してください。GUIは保留中の依頼が到着すると表示されます。

## 文章入力

```json
{"name":"human.request","arguments":{"task":{"kind":"input","title":"文章入力","prompt":"文章を入力してください","response_schema":{"type":"object","properties":{"text":{"type":"string"}},"required":["text"]}}}}
```

回答は `{"values":{"decision":"yes"}}` または `{"values":{"text":"入力文章"}}` の形で返ります。

タスクと回答はプロセス終了時に破棄されます。MIT License。

## 承認者モード（AIConductor）

`HUMANPORT_MODE=approver` で起動すると、MCP からは `human.request` / `human.await` /
`human.get` / `human.capabilities` だけが使え、`human.answer` / `human.cancel` /
`human.list` は提供されません。回答は GUI からのみ行えます。AIConductor は
`scripts/mcp/start-humanport-approver` 経由でこのモードを使い、承認対象の正規化 action を
`detail` 欄に表示します。
