# Agent and delivery workflow

Root `AGENTS.md` is mandatory policy. `harness/README.md` defines progressive context loading; `reports/README.md` defines planning and evidence gates.

For a client batch: answer factual questions first; group related defects by user flow; create one active task card per coherent change; write a draft plan; apply every clarification to that plan; implement only after explicit approval.

Multica is issue/status source. Before code changes, use `ast-index`; use frontend skill for frontend work. UI tasks need desktop/mobile proof; backend tasks need focused test/contract evidence. Production is a separate approved release task.

Lifecycle roles are deliberately separate even when one agent performs them:
planner defines an approved contract; implementer records only facts; tester
records reproducible evidence; reviewer is an independent skeptic. Reviewer
must inspect the approved plan and entire diff, rerun key proof, test
permissions/migrations/Admin/UI consistency and record every finding in
`reports/review-<slug>.md`. An implementation report is evidence to verify,
not a basis for approval.
