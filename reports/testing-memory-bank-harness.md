# Testing: project documentation harness

- Status: passed
- Date: 2026-11-08
- Slug: memory-bank-harness
- Plan: `reports/plan-memory-bank-harness.md`
- Implementation: `reports/implementation-memory-bank-harness.md`
- Environment: local

## Test matrix

| Acceptance criterion | Method / command | Result | Evidence |
| --- | --- | --- | --- |
| Required docs and harness files exist | PowerShell `Test-Path` list | pass | `Harness document checks passed.` |
| Plan is approved before implementation | `Select-String 'Status: approved' reports/plan-memory-bank-harness.md` | pass | Same command exited 0 |
| Harness remains task-scoped, not memory dump | `Select-String 'not project memory' harness/README.md` | pass | Same command exited 0 |
| No tracked diff whitespace errors | `git diff --check` | pass | Exit code 0 |

## Automated checks

```powershell
$harnessPaths = @('docs/INDEX.md','docs/project/overview.md','docs/project/current-state.md','docs/product/backlog.md','docs/architecture/context.md','docs/architecture/containers.md','docs/adr/README.md','harness/README.md','harness/tasks/templates/task.md','harness/context/templates/active-context.md','harness/tasks/active/README.md','harness/tasks/archive/README.md','harness/context/active/README.md','reports/plan-memory-bank-harness.md')
$missingPaths = $harnessPaths | Where-Object { -not (Test-Path $_) }
if ($missingPaths) { $missingPaths; exit 1 }
if (-not (Select-String -Path 'reports/plan-memory-bank-harness.md' -Pattern 'Status: approved' -Quiet)) { exit 1 }
if (-not (Select-String -Path 'harness/README.md' -Pattern 'not project memory' -Quiet)) { exit 1 }
git diff --check
```

Result: `Harness document checks passed.`; process exit code 0.

## E2E scenarios

Not applicable: no runtime behaviour changed.

## Desktop and mobile visual checks

Not applicable: no UI changed.

## Not run and why

- Django, frontend and Docker checks not run: code, dependencies and runtime
  configuration were unchanged.

## Defects and residual risk

- Markdown links were designed as repository-relative paths; automatic
  full-link crawling is deferred until real usage proves validation needs.
- Existing historical docs can still be stale; `current-state.md` explicitly
  requires direct evidence before release decisions.

## Handoff to review

User should review reading order, folder names and rule that Multica owns
execution statuses.
