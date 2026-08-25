# HumanPort MCP Specification v0.1

Status: Draft / implementation specification

## 1. Purpose

HumanPort provides a standard MCP-facing interface for inserting humans into AI-agent workflows.

The MCP server accepts structured requests from an orchestrator, renders them as a human-friendly task, waits asynchronously or synchronously for a response depending on the selected tool, validates the response, and returns structured JSON.

HumanPort SHOULD make a human participant look like a typed capability endpoint rather than a special case in the orchestration engine.

## 2. Design goals

1. Treat human judgment as a normal callable capability.
2. Hide raw JSON from ordinary users.
3. Preserve strict machine-readable input and output schemas.
4. Support approvals, choices, reviews, questions, edits, signatures/attestations, and escalation.
5. Support long human response latency without blocking the server process.
6. Record latency, decision, routing, overrides, and audit events.
7. Allow an orchestrator to compare human calls with AI/tool alternatives by latency, cost, authority, and reliability.
8. Keep the first implementation small enough to run locally.
9. Avoid coupling the core to one UI transport.
10. Make authorization and accountability explicit.

## 3. Non-goals for v0.1

- Human identity proofing beyond a simple local authentication mechanism.
- Legally binding electronic signatures.
- Payroll, HR, or other organization-specific workflow logic.
- Automatic replacement of human decisions by an AI model.
- A general BPM/workflow engine.

## 4. Conceptual architecture

```text
AI Orchestrator
      |
      | MCP tool call
      v
+-----------------------+
| HumanPort MCP Server  |
|-----------------------|
| request validation    |
| task queue            |
| policy/routing        |
| response validation   |
| audit/metrics         |
+----------+------------+
           |
           | internal API / event stream
           v
+-----------------------+
| Human UI Adapter      |
|-----------------------|
| Web UI (v0.1)         |
| future: Slack/mobile  |
+----------+------------+
           |
           v
         Human
```

The MCP-facing layer MUST NOT depend directly on HTML/UI code. A task queue/domain layer sits between MCP tools and presentation adapters.

## 5. Core domain objects

### 5.1 HumanTask

A HumanTask represents one request for human participation.

Required fields:

- `task_id`: UUID
- `kind`: task type
- `title`: short human-readable title
- `prompt`: human-readable explanation
- `created_at`: RFC 3339 timestamp
- `status`: state enum
- `priority`: `low | normal | high | critical`
- `requester`: logical caller identity
- `response_schema`: JSON Schema for structured response

Optional fields:

- `context`: structured supporting information
- `choices`: predeclared options
- `deadline`
- `assignee`
- `required_role`
- `authority_required`
- `risk_level`
- `confidentiality`
- `attachments`
- `correlation_id`
- `idempotency_key`
- `metadata`

### 5.2 HumanResponse

Required fields:

- `task_id`
- `status`: `answered | rejected | expired | cancelled`
- `responded_at`
- `actor`

Optional fields:

- `decision`
- `values`
- `comment`
- `confidence`
- `reasoning_summary`
- `attachments`
- `delegated_to`

`reasoning_summary` is an optional user-written explanation. HumanPort MUST NOT require private chain-of-thought style reasoning.

## 6. Task kinds

v0.1 MUST implement the following kinds:

### `approval`
Binary or multi-state authorization decision.

Typical result:

```json
{
  "decision": "approve",
  "comment": "Within budget."
}
```

### `choice`
Select one or more choices from a constrained list.

### `input`
Collect typed fields using JSON Schema.

### `review`
Display an artifact or structured proposal and collect `accept`, `reject`, or `revise` plus comments.

### `edit`
Ask a human to return edited text or structured values.

### `attestation`
Explicit acknowledgement such as "I have reviewed this." This is NOT a legally binding signature in v0.1.

### `escalation`
Route an unresolved or exceptional case to a human role.

## 7. MCP tools

The first implementation SHOULD expose the following MCP tools.

### 7.1 `human.request`

Create a human task and return immediately.

Input:

```json
{
  "kind": "approval",
  "title": "Approve GPU purchase",
  "prompt": "Approve purchase of a GPU for 128,000 JPY?",
  "priority": "normal",
  "requester": "procurement-orchestrator",
  "context": {
    "amount_jpy": 128000,
    "purpose": "experiment"
  },
  "response_schema": {
    "type": "object",
    "properties": {
      "decision": {"type": "string", "enum": ["approve", "reject", "revise"]},
      "comment": {"type": "string"}
    },
    "required": ["decision"]
  }
}
```

Output:

```json
{
  "task_id": "...",
  "status": "pending",
  "created_at": "..."
}
```

### 7.2 `human.await`

Wait for a task result up to a bounded timeout.

Input:

```json
{
  "task_id": "...",
  "timeout_ms": 30000
}
```

Output is either a completed HumanResponse or:

```json
{
  "task_id": "...",
  "status": "pending"
}
```

The server MUST cap `timeout_ms`; v0.1 recommended cap: 60 seconds.

### 7.3 `human.get`

Retrieve current task state and response if available.

### 7.4 `human.cancel`

Cancel a pending task if policy permits.

### 7.5 `human.list`

List tasks visible to the caller, with filters such as status, kind, priority, assignee, and time range.

### 7.6 `human.capabilities`

Return declared human endpoints/roles and operational metadata suitable for orchestration decisions.

Example:

```json
{
  "endpoints": [
    {
      "id": "manager",
      "roles": ["budget_approval", "policy_exception"],
      "authority": ["purchase_under_500000_jpy"],
      "expected_latency_ms": 7200000,
      "availability": "unknown",
      "cost_class": "high"
    }
  ]
}
```

This information is advisory. Authorization MUST still be enforced server-side.

## 8. State machine

```text
created
  |
  v
pending -------> cancelled
  |                  ^
  |                  |
  +--> assigned -----+
  |       |
  |       v
  |    viewed
  |       |
  |       v
  +----> answered
  |
  +----> rejected
  |
  +----> expired
```

Normative status values:

- `pending`
- `assigned`
- `viewed`
- `answered`
- `rejected`
- `expired`
- `cancelled`

Terminal states: `answered`, `rejected`, `expired`, `cancelled`.

All transitions MUST be audit logged.

## 9. Human-facing UI

v0.1 SHOULD provide a local Web UI.

Minimum screens:

1. Inbox: pending tasks ordered by priority/time.
2. Task detail.
3. Dynamic form generated from `response_schema`.
4. Completed-task history.
5. Basic metrics dashboard.

UI requirements:

- Never require users to edit JSON directly.
- Show title, prompt, requester, priority, deadline, context, and risk prominently.
- Render enums as radio/select controls.
- Render booleans as clear yes/no controls.
- Render strings as text input/textarea depending on hints.
- Validate before submission.
- Require an explicit final submit action.
- Warn when a task has already been answered/cancelled.
- Support Japanese and English text content from the beginning; UI chrome MAY initially be English-only if localization boundaries are clean.

## 10. Schema/UI hints

HumanPort SHOULD accept a `ui_schema` alongside standard JSON Schema for presentation hints without changing response semantics.

Example:

```json
{
  "comment": {
    "widget": "textarea",
    "rows": 5
  },
  "decision": {
    "widget": "radio"
  }
}
```

Unknown hints MUST be ignored safely.

## 11. Routing and authority

A task may contain:

- `assignee`: exact human endpoint
- `required_role`: role/capability
- `authority_required`: authority predicate

The server MUST enforce authorization independently of the orchestrator.

An AI MUST NOT be able to claim a human identity or authority merely by setting request fields.

Example policy:

```text
amount_jpy <= 100000       -> role: team_lead
100000 < amount <= 500000  -> role: manager
amount > 500000            -> role: director
```

Policy implementation SHOULD be modular and MUST be auditable.

## 12. Latency, cost, and quality metrics

HumanPort MUST measure at least:

- `queue_latency_ms`: creation -> assignment/view
- `response_latency_ms`: creation -> terminal response
- `active_latency_ms`: first view -> response
- `timeout_count`
- `cancellation_count`
- `override_count` when an upstream system records an override

Optional orchestrator-facing attributes:

- `expected_latency_ms`
- `cost_class`: `low | medium | high`
- `reliability_score`: 0..1
- `availability`
- `authority`

HumanPort SHOULD distinguish measured statistics from configured estimates.

The system MUST NOT optimize away legally/policy-required human approval merely because latency is high.

## 13. Audit log

Every state-changing operation MUST generate an append-only audit event.

Audit event fields:

- `event_id`
- `timestamp`
- `task_id`
- `event_type`
- `actor_type`: `human | ai | system`
- `actor_id`
- `requester_id` if relevant
- `old_status`
- `new_status`
- `metadata`

Sensitive response content SHOULD NOT be duplicated unnecessarily in audit logs. Store references/hashes where sufficient.

## 14. Idempotency and concurrency

`human.request` SHOULD support `idempotency_key`.

If the same requester repeats the same idempotency key within the configured retention period, the server SHOULD return the existing task rather than create another.

Response submission MUST use optimistic concurrency or an equivalent transactional guard so two users cannot both complete the same task.

## 15. Timeouts and deadlines

`deadline` is semantic and may cause a task to become `expired`.

`human.await.timeout_ms` is transport waiting time only and MUST NOT cancel or expire the task.

This distinction is mandatory.

## 16. Security requirements

Minimum v0.1 requirements:

- Bind Web UI to localhost by default.
- CSRF protection for browser form submission.
- Session authentication.
- Authorization check on every task read/write.
- Escape/sanitize untrusted rendered content.
- No arbitrary HTML from task prompts by default.
- Bounded payload size.
- Bounded attachment size if attachments are enabled.
- Secrets MUST NOT be logged.
- Response schema validation server-side.
- Rate limiting or basic abuse protection on task creation.

## 17. Privacy

Task context can contain sensitive organizational information.

The implementation SHOULD support a `confidentiality` field:

- `public`
- `internal`
- `confidential`
- `restricted`

v0.1 MAY treat this as metadata but MUST preserve it end to end so later adapters can enforce it.

## 18. Storage

v0.1 recommended storage: SQLite.

Suggested tables:

- `tasks`
- `responses`
- `audit_events`
- `users`
- `roles`
- `user_roles`
- `idempotency_keys`

Use migrations from the first commit.

## 19. Transport and deployment

Recommended v0.1 modes:

1. MCP server over stdio for local Codex/agent use.
2. Local HTTP server for the Web UI/internal API.

The MCP process MAY launch the Web service in the same executable, but domain logic should remain separable.

Future transports:

- Streamable HTTP MCP
- Slack
- Teams
- email
- mobile push

## 20. Error model

All tool errors SHOULD return stable machine-readable codes.

Suggested codes:

- `INVALID_REQUEST`
- `INVALID_SCHEMA`
- `TASK_NOT_FOUND`
- `NOT_AUTHORIZED`
- `ALREADY_COMPLETED`
- `TASK_EXPIRED`
- `TASK_CANCELLED`
- `WAIT_TIMEOUT`
- `INTERNAL_ERROR`

Human rejection is a normal domain result, NOT a protocol error.

## 21. Observability

Structured logs SHOULD include:

- request correlation ID
- task ID
- tool name
- duration
- outcome/error code

Metrics SHOULD be exportable later; v0.1 MAY expose JSON metrics through the admin UI.

## 22. Recommended implementation language

Rust is recommended for the first implementation because HumanPort is a long-running infrastructure component with concurrency, typed schemas, local deployment, and a small memory footprint.

Suggested Rust stack:

- `tokio` — async runtime
- MCP SDK/library selected after checking the currently maintained Rust MCP ecosystem
- `axum` — Web UI/API
- `serde` / `serde_json`
- `jsonschema` — response validation
- `sqlx` + SQLite
- `uuid`
- `time` or `chrono`
- `tracing`
- `tower-http`

Do not hard-code an MCP crate until Codex verifies its current maintenance status and protocol compatibility.

## 23. Suggested repository structure

```text
humanport/
  Cargo.toml
  README.md
  crates/
    humanport-core/
    humanport-mcp/
    humanport-web/
    humanport-store/
  migrations/
  web/
  tests/
  docs/
```

For a smaller v0.1, a single crate with modules is acceptable, provided domain/MCP/Web/storage boundaries are maintained.

## 24. Minimum viable prototype

MVP is complete when all of the following work:

1. Agent calls `human.request` via MCP.
2. Task appears in browser inbox.
3. Human opens task and answers a generated form.
4. Server validates answer against JSON Schema.
5. Agent gets result via `human.get` or `human.await`.
6. Audit log records the complete state transition.
7. Metrics report response latency.
8. Duplicate submissions are prevented.
9. Server restarts without losing pending tasks.

## 25. Acceptance test scenario

### Scenario A: purchase approval

Agent creates:

```json
{
  "kind": "approval",
  "title": "Purchase approval",
  "prompt": "Approve purchase of equipment for 128,000 JPY.",
  "requester": "test-agent",
  "priority": "normal",
  "response_schema": {
    "type": "object",
    "properties": {
      "decision": {
        "type": "string",
        "enum": ["approve", "reject", "revise"]
      },
      "comment": {"type": "string"}
    },
    "required": ["decision"]
  }
}
```

Expected flow:

```text
request -> pending -> viewed -> answered
```

Expected response example:

```json
{
  "task_id": "...",
  "status": "answered",
  "responded_at": "...",
  "actor": "local-user",
  "values": {
    "decision": "approve",
    "comment": "Approved within budget."
  }
}
```

### Scenario B: timeout

`human.await` returns `pending` after its transport timeout. The underlying task remains pending.

### Scenario C: concurrent submit

Two browser sessions attempt to answer the same task. Exactly one succeeds; the other receives `ALREADY_COMPLETED`.

## 26. Future extensions

- Multi-human quorum decisions.
- Sequential approvals.
- Delegation.
- Human reputation/skill models.
- Escalation ladders.
- SLA-aware routing.
- AI-suggested default answers displayed distinctly from human-entered answers.
- Side-by-side AI recommendation vs human decision.
- Human/AI disagreement analytics.
- Adapter SDK.
- Mobile client.
- Organization directory integration.
- Cryptographic attestation/signing.
- Policy engines such as Cedar/OPA.
- Task redaction by role.
- Experimental orchestrator policies that choose between AI and HumanPort based on cost/latency/authority.

## 27. Research metrics

For experiments examining when human judgment remains useful, log sufficient data to derive:

- percentage of workflows invoking HumanPort
- call rate by task kind
- median/p95 human latency
- abandonment/expiration rate
- human-vs-AI disagreement rate where an AI recommendation is available
- human override rate
- downstream success rate after human decision
- decisions that require authority even when an AI recommendation is high-confidence

A key research rule is to distinguish:

1. **Human needed for epistemic quality** (better judgment), and
2. **Human required for institutional authority/accountability**.

Those are not the same phenomenon and SHOULD be separately represented in data.

## 28. Compatibility principle

HumanPort should use standard MCP primitives wherever practical. HumanPort-specific fields belong in tool schemas and domain objects; avoid unnecessary protocol forks.

The implementation must check the current MCP specification and currently maintained SDKs before locking protocol details, because MCP continues to evolve.

---

End of HumanPort MCP Specification v0.1
