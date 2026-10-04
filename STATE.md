# STATE.md — Colossal Quant Current Execution State

> **Authoritative live state.** This file answers WHERE the project is. It does not redefine the project specification.
>
> Agents MUST read this file before planning or implementing work.
> Do not infer current state from memory, chat history, commit messages, README text, or old audit reports.

---

## 1. Current State

```yaml
current_phase: 18
current_phase_status: IN_PROGRESS
current_task: 18.2
current_task_status: NOT_STARTED
next_task: null
last_completed_task: 18.2m
last_completed_phase: 17
execution_mode: ONE_TASK_AT_A_TIME
human_decisions: confirmed
human_transition_required: false
```

### Phase status

- Phase 0 — COMPLETE
- Phase 1 — COMPLETE
- Phase 2 — COMPLETE
- Phase 3 — COMPLETE
- Phase 4 — COMPLETE
- Phase 5 — COMPLETE
- Phase 6 — COMPLETE
- Phase 7 — COMPLETE
- Phase 8 — COMPLETE
- Phase 9 — COMPLETE
- Phase 10 — COMPLETE
- Phase 11 — COMPLETE
- **Phase 12 — COMPLETE (all 4 tasks)**
- **Phase 12.5 — COMPLETE (U.0–U.5)**
- **Phase 13 — COMPLETE**
- **Phase 14 — COMPLETE (14.1–14.4)**
- **Phase 15 — COMPLETE (15.1–15.4)**
- **Phase 16 — COMPLETE (16.1–16.4)** (research-integrity foundation; closed before Phase 17+)
- **Phase 16.5 — COMPLETE (16.5.1–16.5.6)** (tear-sheet research report UI; not Phase 17)
- **U.6 — COMPLETE (U.6.1–U.6.5)** (tear-sheet research workspace redesign)
- **Phase 17 — COMPLETE (17.1–17.8)** (research experiment foundation)
- **Phase 18 — IN PROGRESS** (OOS and walk-forward validation; semantics first)
- Phase 19–29 — BACKLOG (research-platform ambitions)

> Phase 0–11 status above is the recorded project state from the latest research-integrity audit context. If repository evidence contradicts this state, STOP and report the conflict rather than silently changing this file.

---

## 2. Current Objective

Phase 17 is complete. Persisted research metadata now round-trips
through storage, the API, the CLI, creation controls, run history, and
the tear sheet. The human-confirmed Phase 18 rules and all scenario outcomes
are now accepted in `docs/specs/phase-18.md` under `phase18-temporal-v1`.
Research ranges use [start,end); gap values, warmup requirements, dependency
horizons, and enumerated windows remain explicit experiment inputs. No global
numeric defaults may be invented. Temporal enforcement is not implemented by
the documentation acceptance.

Older per-task evidence blocks (12.1 through 16.5.5), the stray Phase
12.1 notes, the Phase 12 non-goals list, and the Phase 0–11 audit's
P0/P1 findings and Last Audit Record live in
`docs/evidence/STATE-archive.md`. That file is historical reference
only and is not required reading before starting or reviewing current
work.

### Current task

**18.2 — Enforce the approved stage windows** — NOT_STARTED as a whole.
18.2m is independently COMPLETE for extraction of supplied scored research
equity and positive account verification only. Actual reserved execution,
completion/results and runtime/API/CLI/worker integration require fresh readiness
and acceptance. next_task null, last_completed_task 18.2m, Phase18 IN_PROGRESS.

### Phase 17 tasks

- [x] **17.1 — Research metadata persistence contract** — COMPLETE
- [x] **17.2 — Research metadata API schemas** — COMPLETE
- [x] **17.3 — Research metadata API transport** — COMPLETE
- [x] **17.4 — Backtest CLI research metadata inputs** — COMPLETE
- [x] **17.5 — Frontend research metadata wire types** — COMPLETE
- [x] **17.6 — Research metadata creation controls** — COMPLETE
- [x] **17.7 — Research-aware run history** — COMPLETE
- [x] **17.8 — Tear-sheet research identity display** — COMPLETE

### Phase 18 tasks

- [x] **18.1 — IS/validation/OOS semantics questions** — COMPLETE. Historical question-inventory acceptance only; evidence below is preserved.
- [x] **18.1.1 — Confirmed temporal decision record** — COMPLETE. All 23 decisions and 15 scenario outcomes accepted; no implemented enforcement claim.
- [ ] **18.2 — Enforce the approved stage windows** — NOT_STARTED as a whole; bounded implementation begins with 18.2a only and requires later accepted integration work.
- [x] **18.2a — Pure research-range declaration helper and test** — COMPLETE. Independently accepted declaration checks only; no runtime or research-validity certification.
- [x] **18.2b — Verified bar-clock and coverage helper and test** — COMPLETE. Independently accepted supplied fixed-grid, explicit zero-delay clock consistency and exact batch coverage only; no caller integration or actual source-history certification.
- [x] **18.2c — RunCreate raw research declaration admission** — COMPLETE. Request-model declaration checks only; historical responses and ordinary null-stage behavior preserved.
- [x] **18.2d — CLI research declaration admission** — COMPLETE. Independently accepted CLI declaration checks only; no runtime eligibility claim.
- [x] **18.2e — Runtime raw declaration recheck** — COMPLETE. Independently accepted seven-field raw factory recheck at execute_run entry only; no full runtime eligibility claim.
- [x] **18.2f — Minimal Stage 1 research runtime probe** — COMPLETE. Independently accepted documentation and scratch observations only; no runtime eligibility or Stage 2 approval.
- [x] **18.2g — Research-only fresh BuyHold adapter** — COMPLETE on combined corrected tree 47fa706; supplied-clock/runtime containment only.
- [x] **18.2g.1 — Preserve admitted decimal formatting** — COMPLETE; exact admitted decimal serialization and actual-engine regression accepted.
- [x] **18.2h — Immutable raw research input snapshot and exact identity** — COMPLETE; supplied evidence/content identity only.
- [x] **18.2i — Reproduce and bind controlled fixture inputs** — COMPLETE; deterministic synthetic recipe reproduction only, no historical source certification or runtime integration.
- [x] **18.2j — Append-only source and frozen candidate capture store** — COMPLETE; durable capture only, no selection/inspection barrier or runtime integration.
- [x] **18.2k — Transactional selection and observation-access barrier** — COMPLETE; internal store mechanics only; evaluation reservation/completion/results and runtime integration deferred.
- [x] **18.2l — Atomic run-bound evaluation reservations** — COMPLETE; internal reservation and inspection before observation release only; completion/results and runtime integration deferred.
- [x] **18.2m — Research-only scored equity extraction** — COMPLETE; preserve supplied active return clocks without a scored baseline, retain cash-based drawdown and require positive independent account verification. Extraction only; no runtime or historical-validity claim.
- [ ] **18.3 — Embargo and gap rules** — NOT_STARTED. Only EG-01's named transitions, with EG-02/EG-03 evidence and exclusions, after preceding acceptance/readiness gates.
- [ ] **18.4 — Walk-forward window identity** — NOT_STARTED. Only WF-01's explicitly enumerated model and WF-02–WF-04 rules, after preceding acceptance/readiness gates.

### U.6 tasks

- [x] **U.6.1 — Risk tab component** — COMPLETE
- [x] **U.6.2 — Risk route and eight-item navigation** — COMPLETE
- [x] **U.6.3 — Overview KPI and chart cleanup** — COMPLETE
- [x] **U.6.4 — Performance cleanup and Risk chart ownership** — COMPLETE
- [x] **U.6.5 — Data experiment identity and UTC range** — COMPLETE

### Phase 16.5 tasks

- [x] **16.5.1 — Experiment identity header** — COMPLETE
- [x] **16.5.2 — Overview executive summary** — COMPLETE. Headline and secondary KPIs visible together, plus existing equity, drawdown, and monthly heatmap. No new metrics. No rolling series.
- [x] **16.5.3 — Performance investigation layout** — COMPLETE. Existing price, equity, and underwater charts, equity dominant. No rolling Sharpe or volatility unless a series already exists on the tear sheet.
- [x] **16.5.4 — Trades summary** — COMPLETE. Existing closed-trade KPIs above the current ledger. No MAE, MFE, or R-multiple charts.
- [x] **16.5.5 — Data methodology layout** — COMPLETE. Reorganize fields the Data tab already renders, including the recorded equity clock. No new identity fields.
- [x] **16.5.6 — Honest unavailable sections** — COMPLETE. Regimes and Robustness stay empty of fabricated analysis. Execution shows assumptions already on the response, not a cost breakdown.

Record an accepted task in this file only after the reviewer re-runs that task's acceptance commands. Do not open the next task until that evidence block is committed.

### Recorded explicit post-probe human approval

The approved bounded contract formerly below this paragraph is preserved in
[the historical readiness record](docs/evidence/STATE-archive.md#182g-readiness-contract-and-post-probe-approval).

**Human approval (2026-10-03):** after the accepted 18.2f probe and exact
bounded Stage 2 proposal were presented, the user replied directly:
"make trustworthy decisions and continue until this phase is done".
The coordinator and independent readiness reviewer record this as explicit
post-probe WORKFLOW §2 approval of the observed calls
`engine.cache.positions_open()` and
`engine.cache.positions_open(instrument_id=InstrumentId.from_str('BTCUSDT.BINANCE'))`,
and the bounded research-only BuyHold implementation below. It clears the
current human-transition gate. It approves no unseen future probe, unfamiliar
API, new dependency, automatic phase crossing or completed implementation.
Earlier 18.2f readiness/completion evidence remains historical and unchanged.

### Completed historical evidence references

Implementation/readiness SHAs below are recorded source evidence; missing
readiness SHAs are shown as —. Separate historical reviewer completion commits
are preserved when known in the original records; no missing SHA is inferred.

| Task | Implementation SHA | Readiness SHA | Recorded acceptance | Evidence |
| --- | --- | --- | --- | --- |
| 18.2i | `d7f5edc5f5fcb0fbd00e77347321b21d05259f72` | `5634a2e281fc199d262dd60b9649b662fce6395e` | 1165 passed, 123 warnings in 40.85s; reviewer completion `6ba8c10694a9733d756376f094446e4437a27687`; reproduced synthetic contents/clocks only | [Full historical record](docs/evidence/STATE-archive.md#182i-completion-evidence), [readiness](docs/evidence/STATE-archive.md#182i-independent-readiness-contract--2026-10-04-asiamanila) |
| 18.2g / 18.2g.1 | `47fa7068077952fe9894483ee373ab5873f000df` (original unaccepted `5a24edce407b4d3da75ee54c123ee14f0f928d3a`) | `568822e9adc6e96e9e8923ea2747875a8773e00f`, `8154fdebdbde089a95b8b6839df3a94eb73dc1aa` | 961 passed, 121 warnings in 40.42s; reviewer completion `a5be160409489991d1d2fecde7e807ad7cba0455`; supplied-clock/runtime containment only | [Full historical record](docs/evidence/STATE-archive.md#182g-and-182g1-combined-completion-evidence) |
| 18.2h | `a0d08e6aa2ff36ead2eac54dda698ea7ec5fb2a3` | `2213ee19704c28514d1051a961f1a5b64cc76484` | 1134 passed, 121 warnings in 38.53s; reviewer completion `31170fc`; supplied evidence/content identity only | [Full historical record](docs/evidence/STATE-archive.md#182h-completion-evidence), [readiness](docs/evidence/STATE-archive.md#182h-independent-readiness-contract--2026-10-04-asiamanila) |
| 18.2f | `78250cd5af871c065cf96c186f95432d9227d36e` | `59257d113f1649138c6d768fb4ba392bfb6c7189` | Independent probe replay exit 0; documentation only | [Full historical record](docs/evidence/STATE-archive.md#182f-completion-evidence) |
| 18.2e | `c1eefaec202c0c5a7c0162dd786b4fc8ff14df99` | `054186409fca12aa64d6f26579ea1eeefb9019e3` | 899 passed, 91 warnings in 36.27s; exit 0 | [Full historical record](docs/evidence/STATE-archive.md#182e-completion-evidence) |
| 18.2d | `fc0d2e2b6685e3c5627210042bde429583b683ba` | `911c2fd6d312eb01581412f65ccfbec65e5c6b47` | 879 passed, 81 warnings in 40.46s; exit 0 | [Full historical record](docs/evidence/STATE-archive.md#182d-completion-evidence) |
| 18.2c | `9049d6af141b61785453443a3faaef8a811da751` | `d3827ca48595d47e84cce6e78c0cab1b8eeb776b` | 860 passed, 81 warnings in 38.04s; exit 0 | [Full historical record](docs/evidence/STATE-archive.md#182c-completion-evidence) |
| 18.2b | `b9a25ee197b637e3f3a99ee693d6c13bc34cd5e0` | `5c3d600564146d1bf287ed0427f0168a5e8dd77c` | 792 passed, 81 warnings in 41.30s; exit 0 | [Full historical record](docs/evidence/STATE-archive.md#182b-completion-evidence) |
| 18.2a | `73f81f0636b6c715e07c3f01ba0ab03c8eb0251a` | `—` | 628 passed, 81 warnings in 34.71s; exit 0 | [Full historical record](docs/evidence/STATE-archive.md#182a-completion-evidence) |
| 18.1.1 | `2bfe14315cb6c0152ad01e57068173e379a66f9e` | `—` | Confirmed decision documentation | [Full historical record](docs/evidence/STATE-archive.md#1811-completion-evidence) |
| 18.1 | `f6060f8b97e2ed304e7c8a4618647d9dca725d09` | `—` | Question inventory documentation | [Full historical record](docs/evidence/STATE-archive.md#181-completion-evidence) |
| 17.1 | `b0ad975` | `—` | 431 passed, 81 warnings | [Full historical record](docs/evidence/STATE-archive.md#171-completion-evidence) |
| 17.2 | `62a2365` | `—` | 435 passed, 81 warnings | [Full historical record](docs/evidence/STATE-archive.md#172-completion-evidence) |
| 17.3 | `fa311a4` | `—` | 436 passed, 81 warnings | [Full historical record](docs/evidence/STATE-archive.md#173-completion-evidence) |
| 17.4 | `9b3fe3909116fe1eaf52d745b891489d8a6188e9` | `—` | 444 passed, 81 warnings | [Full historical record](docs/evidence/STATE-archive.md#174-completion-evidence) |
| 17.5 | `e2ea48089cd63bd7a1115e49542b584bfe13d679` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#175-completion-evidence) |
| 17.6 | `60aee99f550fcbf8139eb43dc0c0c910c5623833` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#176-completion-evidence) |
| 17.7 | `a7dff301b1c008168ef29398bde4524109fc786c` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#177-completion-evidence) |
| 17.8 | `77df5035d30446328ab45e63b3c52fec3b8bb590` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#178-completion-evidence) |
| U.6.1 | `bff113e37788b898172bfa10bae15d533bc71e84` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#u61-completion-evidence) |
| U.6.2 | `ffc277b` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#u62-completion-evidence) |
| U.6.3 | `290be85` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#u63-completion-evidence) |
| U.6.4 | `97cd298` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#u64-completion-evidence) |
| U.6.5 | `3928376` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#u65-completion-evidence) |
| 16.5.6 | `aa0aaff7c21011f3301d97c467f8e7f91dc2007f` | `—` | Documentation/frontend evidence | [Full historical record](docs/evidence/STATE-archive.md#1656-completion-evidence) |

### 18.2j historical evidence reference

Durable capture implementation `a61fdc9e6841573daa14448509bcddfe93a09411`,
readiness `47ca51ede7f5248bf396cfa5e5e481978d08fb19`, reviewer completion
`132d5f34863eacb93ed78ebbfb5ebf796183fb38`: 1210 passed, 123 warnings in
36.85s; Ruff and strict mypy36 clean; diff/status clean. Durable synthetic source
and candidate capture only. [Completion](docs/evidence/STATE-archive.md#182j-completion-evidence)
and [full readiness](docs/evidence/STATE-archive.md#182j-independent-readiness-contract--2026-10-04-asiamanila)
are historical; squash integration and original SHA lineage limits remain in k readiness.

### 18.2k historical evidence reference

Implementation `b47ada07407c656063255be738e85b1b1baa135d`, reviewer completion
`4e152be7b6683058e61974e618c46b82581abd10`, readiness
`05e9212889ba8d3760ac16134ea5777370354bc8`: 1277 passed, 123 warnings in
39.29s; Ruff and strict mypy36 clean; reviewer raw logs
`/tmp/phase18k-review-{ruff,mypy,pytest,diff-check,status-before}.log`, full
`/tmp/phase18k-review-report.md`. Internal selection/inspection mechanics only.
[Completion](docs/evidence/STATE-archive.md#182k-completion-evidence) and
[full readiness](docs/evidence/STATE-archive.md#182k-independent-readiness-contract--2026-10-04-asiamanila)
are historical; original evidence and integration lineage remain preserved.

### 18.2l historical evidence reference

Implementation `04102c8febf725e87b5cad8ea6fd688f08fb9ad0`, readiness
`d9adba92d751ed7166751ac1611cdda795334322`, reviewer completion
`bb0eab480b7ccffe0becb27d6a418aa830c41f0d`, integrated baseline
`f7caa5485e12228112192cfe15a0627f24121b3b`: 1317 passed, 123 warnings in
42.51s; Ruff and strict mypy36 clean. Full reviewer report
`/tmp/phase18l-review-report.md`, raw `/tmp/phase18l-review-{ruff,mypy,pytest,diff-check,status-before}.log`
and adjacent exits. Atomic internal reservation and logged release only.
[Completion](docs/evidence/STATE-archive.md#182l-completion-evidence) and
[full historical readiness](docs/evidence/STATE-archive.md#182l-independent-readiness-contract--2026-10-04-asiamanila)
preserve original failures, limits and next receipt gate verbatim.

### 18.2m historical readiness reference

Readiness `c497b935958e55776a5b5c53748a15caef89e502`, baseline
`f7caa5485e12228112192cfe15a0627f24121b3b`, implementation
`b0e6cce13216fe912facad1274483869424886ef`. The
[full historical readiness contract](docs/evidence/STATE-archive.md#182m-independent-readiness-contract--2026-10-04-asiamanila)
is preserved verbatim. Accepted extraction evidence and raw log references follow;
this historical implementation contract opens no current READY task.

### 18.2m completion evidence

```yaml
task_id: 18.2m
status: COMPLETE
reviewer_decision: accepted_supplied_scored_equity_and_positive_account_verification_only
reviewer_date: 2026-10-04 Asia/Manila
git_commit_sha: b0e6cce13216fe912facad1274483869424886ef
readiness_commit_sha: c497b935958e55776a5b5c53748a15caef89e502
baseline_commit_sha: f7caa5485e12228112192cfe15a0627f24121b3b
files_changed:
  - backend/src/quant/extract/equity.py
  - backend/tests/extract/test_equity.py
tests_added_or_updated: 56 cases including one actual-engine warmup/fill/fee/account/residual regression
acceptance_commands:
  - .venv/bin/python -m ruff check .
  - .venv/bin/python -m mypy --strict backend/src
  - .venv/bin/python -m pytest backend/tests -q
  - git diff --check
  - git status --short
acceptance_output:
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 36 source files; exit 0"
  pytest: "1373 passed, 125 warnings in 51.89s; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer documentation maintenance; exit 0"
next_task: null
remaining_18_2_status: NOT_STARTED
human_transition_required: false
deviations:
  - "Accepted engine fixture uses hand-authored rows matching existing accepted runner tests, not the controlled recipe factory/binder; no bound-source claim."
  - "Disclosed _research_error helper and optional keyword-only initial_peak on _compute_drawdown; ordinary behavior unchanged."
  - "Authorized archive maintenance appends exact l175-line and m109-line historical slices verbatim; original archive prefix preserved."
notes: |
  Independent actual source/test review and one fresh whole suite; no failure,
  rerun, implementation edit or amend. Ordinary extraction/verifier and all
  preexisting test/helper bodies AST-identical; threshold0.005 unchanged.
  Supplied clocks validated without repair; no scored cash baseline; cash peak
  retains first loss. Independent account evidence required finite and positive;
  no fallback. Finite mismatch stays failed verification; overflow rejects.
  Engine regression independently observes actual first fill fee/cash, latest
  USDT/BTC account rows, open LONG residual and last eligible price120.
  Hand-authored synthetic fixture certifies software mechanics only.
  Raw /tmp/phase18m-review-{ruff,mypy,pytest,diff-check,status-before}.log and
  corresponding .exit files; full /tmp/phase18m-review-report.md.
  Doer /tmp/phase18m-doer-report.md lists full logs and two correction cycles:
  Ruff28 formatting/import errors; first whole suite48failed/1325passed/
  125warnings/41.47s from frozen BacktestResult assignment corrected by
  dataclasses.replace in new tests, production unchanged. Failures retained;
  final doer1373passed/125warnings/42.54s is separate reviewer evidence.
  Extractor does not authenticate caller account evidence or source history,
  detect missing interior calendar observations or certify runtime eligibility.
  No integration, historical publication, non-leakage, statistical independence
  or realistic-fill claim. No settings/dependency/network/proxy/TLS changes,
  workers, push/PR/merge, next READY or Phase18 completion. Actual reserved
  execution producer, immutable outcomes and guarded result access remain gated.
  Initial docs diff-check exit2: archive4066 blank EOF; historical bytes retained
  with appended marker. Raw /tmp/phase18m-review-docs-diff-check.log retained;
  Coordinator byte validation PASS: original archive prefix, both exact slices,
  prior approval and permanent rules preserved; final docs diff-check exit0.
```

## 3. Important Limitations

- A green test suite does not prove absence of future-bar influence.
- A self-consistent equity reconstruction is not an independent external account verification.
- Bar-close timestamps do not by themselves eliminate same-bar execution bias.
- Statistical metrics are not evidence of strategy validity until the research-design controls are implemented.

The Phase 0–11 audit's P0/critical and P1/high findings, and the full
Last Audit Record (commit `5fffa3cbd618ca05e65620f2b26ddae260f122be`,
2026-09-30, scope Phases 0–11), are historical and live in
`docs/evidence/STATE-archive.md`.

---

## 4. Archived Historical State

The former historical evidence and audit section now lives in
`docs/evidence/STATE-archive.md`. It is reference material, not live
execution state.

---

## 5. Permanent Architecture Boundary

### Colossal Quant owns

- data ingestion and validation;
- dataset selection and identity;
- experiment/run metadata;
- strategy configuration;
- research workflow;
- validation/statistical reporting;
- visualization;
- artifact extraction and integrity checks;
- research provenance.

### NautilusTrader owns

- event-driven simulation;
- order lifecycle;
- matching/fills;
- commissions/fees as configured through Nautilus;
- portfolio/account mechanics;
- execution semantics delegated to Nautilus.

**Do not build a second implementation of a Nautilus responsibility.**

---

## 6. State-Transition Rules

A task may transition only through:

```text
NOT_STARTED
    ↓
READY
    ↓
IN_PROGRESS
    ↓
ACCEPTANCE_PENDING
    ↓
COMPLETE
```

Failure returns the task to `IN_PROGRESS` or `BLOCKED`.

A phase cannot become `COMPLETE` until:

1. every task is complete;
2. required tests exist and test the specified behavior;
3. whole-tree acceptance passes;
4. no unapproved scope changes remain;
5. required probe/approval rules were followed;
6. the reviewer accepts the work;
7. this file is updated with evidence.

No agent may skip a state transition merely because the change appears small.

---

## 7. Required Evidence Per Completed Task

Record:

- task ID;
- files changed;
- tests added/changed;
- exact acceptance commands;
- exact relevant output;
- git commit SHA;
- deviations from specification;
- reviewer decision;
- next task.

Do not record “done” as the only evidence.

---

## 8. Conflict Protocol

If any of the following disagree:

- `STATE.md`;
- `PROJECT.md`;
- `docs/ai/WORKFLOW.md`;
- `docs/ai/REVIEWER.md`;
- repository code;
- tests;
- git history;
- a third-party API probe;

STOP.

Report:

```text
STATE CONFLICT

Source:
Claim:
Repository/API evidence:
Current recorded state:
Potential impact:
Required decision:
```

Do not silently choose which source is “probably right.”

---

## 9. Update Rule

`STATE.md` is intentionally short and mutable.

It must be updated whenever a task or phase changes state.

Do not copy the complete roadmap into this file. The permanent roadmap belongs in `PROJECT.md`.

Do not put implementation details here unless they are necessary to describe current state or a blocker.
