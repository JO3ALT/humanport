# HumanPort MCPプロトコル

`human.request` の `arguments.task` に `kind`、`title`、`prompt` を指定します。選択入力は `kind: "choice"` と `choices: [{"value","label"}, ...]`、文章入力は `kind: "input"` です。

回答は選択なら `values.decision`、文章なら `values.text` に入ります。補助ツールとして `human.get`、`human.await`、`human.cancel`、`human.list`、`human.capabilities` を提供します。状態はメモリ上のみで管理します。
