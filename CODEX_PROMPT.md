# Codex implementation prompt — HumanPort v0.1

Implement the project described in `SPEC.md` as a working Rust MCP server named **HumanPort**.

## Primary objective

Create a local-first Human-in-the-loop MCP server where an AI agent can create a typed request for human judgment, the request appears in a browser UI, a human answers through a generated form, and the validated structured result becomes available to the AI through MCP.

## Read first

1. Read `SPEC.md` completely.
2. Check the current official MCP specification and the currently maintained Rust MCP SDK/library before choosing protocol/library details. Do not assume an old crate or API is current.
3. Keep protocol-specific code behind a small adapter boundary.

## Implementation constraints

- Language: Rust, current stable toolchain.
- Async runtime: Tokio.
- Web: Axum unless a strong technical reason requires another framework.
- Storage: SQLite with migrations.
- Serialization: Serde.
- Structured logging: tracing.
- Default browser binding: localhost only.
- No frontend framework is required for v0.1. Server-rendered HTML plus small amounts of JavaScript are preferred.
- The human must never need to edit raw JSON.
- Validate response data server-side against the supplied JSON Schema.
- Preserve pending tasks across process restarts.

## MCP tools to implement

- `human.request`
- `human.await`
- `human.get`
- `human.cancel`
- `human.list`
- `human.capabilities`

Use exact semantics from `SPEC.md` unless incompatibility with the current MCP protocol requires an adaptation. Document any adaptation.

## Development order

1. Domain types and state machine.
2. SQLite schema and repository layer.
3. Unit tests for state transitions and concurrency.
4. MCP tool handlers.
5. Web inbox and task view.
6. Dynamic response form generation.
7. JSON Schema validation.
8. Audit log.
9. Latency metrics.
10. End-to-end test covering request -> browser response -> MCP result.

## Security baseline

Implement the v0.1 security requirements in `SPEC.md`, including localhost binding, CSRF protection, authorization checks, output escaping, payload bounds, and protection against duplicate submissions.

Do not implement arbitrary HTML rendering from agent-supplied prompts.

## UI

Keep the UI utilitarian and fast:

- Inbox table/cards with priority, age, requester, and task kind.
- Task detail with prompt/context.
- Generated typed form from JSON Schema.
- Explicit Submit button.
- Completed history.
- Metrics page showing at least median/p95 response latency and task counts.

Japanese text in task content must render correctly (UTF-8).

## Tests required

At minimum add automated tests for:

- valid task creation
- invalid schema rejection
- valid response acceptance
- invalid response rejection
- `human.await` timeout does not expire task
- deadline expiration
- cancellation
- duplicate/idempotent request handling
- concurrent double-submit prevention
- authorization failure
- restart persistence

## Deliverables

The repository should contain:

- buildable Rust source
- migrations
- tests
- `README.md` with setup/run instructions
- example MCP client configuration
- example purchase-approval workflow
- architecture notes explaining the domain/MCP/Web/storage boundaries
- a short `ROADMAP.md` for quorum approvals, Slack adapter, role routing, and AI-vs-human metrics

## Definition of done

Do not stop at scaffolding. The MVP is done only when an MCP client can create a task, a browser user can answer it, and the MCP client can retrieve the validated response after server restart if necessary.

Prefer a small working vertical slice over premature abstractions, while keeping adapters/domain separation clear.
