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
current_task: 18.2l
current_task_status: READY
next_task: null
last_completed_task: 18.2k
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

**18.2l — Atomic run-bound evaluation reservations** — READY.
Independent readiness opens only the internal atomic reservation and logged
observation-release task below. Accepted 18.2k mechanics remain complete;
remaining 18.2 is NOT_STARTED as a whole. Completion/results and
runtime/API/CLI/worker integration require fresh readiness and acceptance.
next_task null, last_completed_task 18.2k, Phase18 IN_PROGRESS.

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
- [ ] **18.2l — Atomic run-bound evaluation reservations** — READY; internal reservation and inspection before observation release only; completion/results and runtime integration deferred.
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

### 18.2k completion evidence

```yaml
task_id: 18.2k
status: COMPLETE
reviewer_decision: accepted_internal_store_selection_and_observation_mechanics_only
reviewer_date: 2026-10-04 Asia/Manila
git_commit_sha: b47ada07407c656063255be738e85b1b1baa135d
readiness_commit_sha: 05e9212889ba8d3760ac16134ea5777370354bc8
files_changed:
  - backend/src/quant/data/research_store.py
  - backend/tests/data/test_research_store.py
tests_added_or_updated: 67 actual tmp_path SQLite lifecycle, access, replay, rollback and concurrency cases
acceptance_commands:
  - .venv/bin/python -m ruff check .
  - .venv/bin/python -m mypy --strict backend/src
  - .venv/bin/python -m pytest backend/tests -q
  - git diff --check
  - git status --short
acceptance_output:
  ruff: "All checks passed!; exit 0"
  mypy: "Success: no issues found in 36 source files; exit 0"
  pytest: "1277 passed, 123 warnings in 39.29s; exit 0"
  diff_check: "no output; exit 0"
  status: "no output; clean before reviewer documentation maintenance; exit 0"
next_task: null
remaining_18_2_status: NOT_STARTED
human_transition_required: false
deviations:
  - "Disclosed ContextVar scopes own lifecycle replay integrity errors; finally reset, original source errors and concurrent isolation accepted. No contract deviation."
  - "Authorized reviewer archive maintenance: exact 177-line j completion/readiness slice appended verbatim, original archive prefix preserved; compact live references retained."
notes: |
  Independent actual code/test acceptance; no implementation fixes or amend.
  Same-connection BEGIN IMMEDIATE replay/gates/insert and COMMIT before release;
  historical prefix, exact idempotence, all selection-source/candidate watermarks,
  actor-independent UUID repeat access, shared-clock contamination, criteria-change
  parent lineage and SC15 new IS reuse with new unseen holdout accepted.
  Declared trial budget/criteria and outside-inspection claims remain declarations.
  Scoped error reset, source error preservation and single logging verified.
  One fresh whole suite; no failure/retry/correction. Complete raw logs
  /tmp/phase18k-review-{ruff,mypy,pytest,diff-check,status-before}.log;
  full review /tmp/phase18k-review-report.md. Doer1277/123/41.45s separate;
  initial Ruff12/mypy3 failures and wrapper limitation retained in doer raw logs.
  No integrated runtime/API/CLI/worker guarantee, evaluation/result state,
  historical authenticity, unseen market truth or statistical independence.
  No dependency, worker, publish, merge, next READY or Phase18 completion.
  Coordinator independently byte-validated exact177 slice/archive prefix and
  unchanged k readiness, approval/rules and live SHAs before separate docs commit.
  Initial docs diff check exit2: archive3602 blank EOF; historical bytes retained
  with authored end marker, final docs diff check exit0; raw failure preserved.
  Enabled network/default sandbox/options/proxy/TLS unchanged.
  current_task18.2 NOT_STARTED, last_completed_task18.2k, Phase18 IN_PROGRESS.
```

### 18.2k independent readiness contract — 2026-10-04 Asia/Manila

Independent readiness opens ONLY **18.2k READY**. Verified clean branch
`phase18/18.2k-observation-barrier`, baseline HEAD/refreshed main
`628f836bb9967500b0481e9cbedef29b6f41b0d9`. Independent `git ls-remote origin
refs/heads/main` under use_default returned that exact SHA; this is point-in-time
remote evidence, not a future freshness claim. HEAD has exactly one parent,
`a4d677ca4bd4447f6f1d24ee1261e227d844d517`. The user `colossalshub` squash-merged
PR13 at 2026-10-03 18:23:30 UTC; the coordinator did not merge. `git diff --quiet
c279bc2d7686dfa10bcdad5dc38e2c86385022b5 HEAD` exit 0 establishes the accepted
integration tree is preserved, including the user's `.gitignore` change.
Original source `a61fdc9e6841573daa14448509bcddfe93a09411` and reviewer completion
`132d5f34863eacb93ed78ebbfb5ebf796183fb38` are historical evidence on the preserved
published branch/PR, NOT ancestors of this squash HEAD (both ancestry checks
exit 1). No normal-merge or all-checks-SUCCESS claim is made. The neutral Bugbot
nonfinite-float OverflowError finding was disproved by eight actual SQLite
replays: expected ValueError and one ERROR each; resolved thread and PR body
contain the proof. Raw `/tmp/phase18j-bugbot-review-replay.log` and probe remain
supporting session evidence, not a prerequisite artifact for implementation.

Read full live AGENTS/STATE/WORKFLOW/REVIEWER/INCIDENTS, relevant PROJECT stack,
SQLite/research contracts, execution/conventions, Phases16–18, completion and AI
rules; full confirmed Phase18 spec, project/backend rules, existing store/test,
fixture/input membership and accepted coverage contracts. Same stdlib SQLite
connection pattern, json/hashlib/time plus uuid4, no unfamiliar third-party
calls or dependencies; no probe required. Human delegated trustworthy routine
choices and continuation authorize this conservative refinement. All previous
approval, rules and j readiness/completion records remain byte-preserved.

This contract governs implementation, superseding disposable planning notes and
narrowing the historical j next-extension reservation/result language: ONLY
selection and observation-access logging now; separately gated evaluation
reservation/completion/result publication afterward, then runtime/API/CLI/worker
binding and guarded public access. The lifecycle table is private schema support
inside the existing store connection, not a separate migration/orchestration
project. One existing implementation file plus its mirrored test is the bounded
reviewable deliverable. No archive maintenance or implementation in readiness.

## Bounded usable scope

Implement actual store operations that atomically freeze selection and log observation release BEFORE returning data. Separate later task handles evaluation reservation/completion and guarded result publication: do not invent completed results or certify evaluation from an input access event. Each repeated observation release gets a distinct access event, marked repeat access, never independent evidence. Runtime/API integration must use these operations later; no integrated OOS guarantee claimed now. No new public unloggedrawgetter.

## New public internal APIs

Frozen slots ResearchLifecycleEvent(seq:int,event_id:str,kind:Literal['selection','inspection'],recorded_at_ts:int,canonical_bytes:bytes); ResearchObservationAccess(event:ResearchLifecycleEvent,observations:tuple[ResearchObservation,...]). Direct construction unvalidated; noeligibleflag.
freeze_final_selection(db_path:Path, *, document:Mapping[str,object])->ResearchLifecycleEvent
access_validation_observations(db_path:Path, *, candidate_id:str,input_id:str,start_ts:int,end_ts:int,actor:str)->ResearchObservationAccess
access_oos_observations(db_path:Path, *, selection_id:str,actor:str)->ResearchObservationAccess
record_external_inspection(db_path:Path, *, input_id:str,start_ts:int,end_ts:int,actor:str,declared_at_ts:int | None,note:str)->ResearchLifecycleEvent

Every returnedtuple contains ONLY explicitly requested halfopenclosemembers, never fullsnapshot/recipe/selectiondata. Publiccapture records j remain internal and MUSTNOT be blindly serialized by futureAPI. Privateconnectionreplay used inside samewritetransaction; no pathreplaynestedconnection. No publiclifecycle rawpayloadread added.

## Storage/order/identity

New research_lifecycle_v1 table(seq INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT UNIQUE NOT NULL,kind TEXT CHECKkindselection/inspection,recorded_at_ts INTEGER NOT NULL,payload BLOB NOT NULL,selection_revision TEXT,experiment_id TEXT,hypothesis_id TEXT), UNIQUE(experiment_id,hypothesis_id,selection_revision); nullindexedfields forinspections. UPDATE/DELETEtriggers sameappend-onlypattern. Sourceevents unchanged. Everylifecyclemutation BEGINIMMEDIATE, replaysource/candidate/lifecycleintegrity, performchecks, append,COMMIT before returning observations; failureROLLBACK no release. Sameconnection bothtables.

Lifecycle serverseq authoritative for lifecycleordering; sourceeventseq distinctdomain. Every inspection records source_watermark=MAX(research_events_v1.seq) in same transaction. Thus candidate.seq<=inspection.source_watermark proves candidate alreadycommitted at release/manualreport; do not compare independentseqdomains or walltimes. Wallrecorded_at=time.time_ns//1000000 canrollback/repeat, never callerbackdated. Manualdeclaredtime is an attributed claim stored separately; cannot undo contamination or establishactualinspectiontime.

Canonical sortedcompactUTF8JSON, acceptedtypedhexALLnumbers, noBOM/newline, eventidSHA256prefix. Selectioncontentid deterministic/idempotent exactrecapture preservingoriginalseq even after laterinspection; NEW selectionrevision cannot use inspectedholdout. Each inspection payload includes server-generateduuid4.hex access_id so everycall distincteventid, action validation/oos/external, actor, declared_at_ts (nullforsoftwareaccess), note(nullforsoftwareaccess), input_id,bounds,source_watermark, subject membership, candidate_id/selection_id applicable elseNone. Fixed contractversions research-selection-v1/research-inspection-v1 andrulephase18-temporal-v1. Typedreplay verifiesdigest/canonicalencoding/indexedcolumns/references/subjectmembership; malformedpersistentdatafailintegrity, no hashtrustshortcut. Existing j decode/replay semantics preserved.

## Exact final selection document

Requiredkeys ONLY contract_version,rule_id,experiment_id,hypothesis_id,selection_revision,selected_candidate_id,considered_candidate_ids,selection_criteria,validation,input_id,oos_start_ts,oos_end_ts. selection_criteria explicitnonemptytext (criteriaidentity/recipe declaration, not inferred frombestmetric). IDs/textvalidUTF8/noNUL/surrogates,nounrequestedtrim. considered_candidate_ids nonemptylist/tupleuniqueIDs; orderretained. validation explicitNone OR exact {input_id,start_ts,end_ts}; this one commonrange is permitteddevelopmentvalidation for all consideredcandidates. input_id is finalholdoutcapturedsourceevent; oosbounds integerexcludingbool,start<end,gridaligned, actualexactcoverage. No globalnumericdefault/gap/window inferred.

All consideredids replay validfrozencandidates fromsameexperiment/hypothesis; selectedid occurslist. Each declares sametrial_count N==listlength, trial_indexexactset1..N; binds exact immutable parameters/code/seed/artifacts/ISinput/ranges via candidateids, not duplicatecaller overrides. Existing assertions retained; runtime later verifies actualexecutingcode/params exactly. No optimizerallowed. Complete selectiondata identity consists eachcandidateISinput+ISbounds and optionalcommonvalidationinput+bounds; actualmembertuples derived/persisted, not callerhash. If validationused, require everycandidate previouslypassed access_validation_observations on exactlythatinput/range, committedbeforeselection; require candidate existed before ANY earlier inspection of thatvalidationmembership (usinginspection watermark). If skippedNone require no validationaccess forconsideredcandidates (explicitskip, not ambiguoushiddenuse).

IS precedes validation ifpresent; validation precedesOOS else everyIS precedesOOS. Touchingendpoints allowed withoutgapguarantee. Every selectionIS/commonvalidation membership disjoint finalOOS membership; noholdoutobservationsallowedselection even ifinputIDrenamed. Any priorinspection of finalOOSsubject membership (software/manual, anyactor/experiment) prevents NEWselectionfreeze. Existingexactselectionrecapture idempotent, doesnot permit alteredfreeze afterinspection. Exactcurrentselectedcandidateandselectionmetadata retained forever. No publicOOSaccess canoccur without committedselection event.

## Criteria-change lineage and claim limits

For NEW selection revisions, compare selection_criteria with the latest earlier committed selection in the same experiment/hypothesis (highest lifecycle seq; historical replay uses only its earlier prefix). If criteria differ, selected_candidate_id must differ and its validated earlier-committed parent chain must reach the previous selected_candidate_id. Otherwise raise exactly `changed selection criteria require a new candidate revision with prior selection lineage`. Run after chronology and before validation access proof. Exact original recapture returns before this current gate. Test actual SQLite rejection of changed criteria with same selected candidate or unrelated replacement, acceptance of linked new candidate with unseen holdout, and preserved prior selection. This implements ST-02 without adding candidate fields or inventing optimizer results.

The declared considered list and N/index set validate the declared trial budget only. They cannot prove all human-considered alternatives were recorded; unlogged/manual alternatives remain unverified (Phase19 multiple-testing controls are outside scope). Criteria text is an attributed declaration, not proof of actual optimization or selection outcomes. All claimed validation proof is logged committed access to the exact range for each declared considered candidate.

## Exact persisted payloads and replay

Selection payload EXACT keys: contract_version,rule_id,document,candidate_bindings,selection_memberships,holdout_membership. document is the exact validated finalselection document above, with integerpositions typedhex (oosbounds and nestedvalidationstart/end), tupleconsidered canonicalizedlist. candidate_bindings ordered list matching consideredids; each exact {candidate_id,candidate_payload}, candidate_payload parsed exact immutablecanonicalcandidate JSON (alreadytypedcash/IS/trialnumbers), binding actualparams/code/seed/artifacts/trial/ISreferences without caller-overrides. selection_memberships orderedlist one per candidateIS, then commonvalidation ifused, each exact {role,candidate_id,input_id,start_ts,end_ts,members}; role='is'/'validation', candidate_id null onlycommonvalidation. holdout_membership exact {input_id,start_ts,end_ts,members}. Bounds typedhexints. No rawOHLCV/recipe leaked in these metadata structures. Candidate/input IDs reference internalsourceevents and are integrity-replayed.

Each members value is a chronological unique list of fixed6elementarrays [venue,symbol,timeframe,source_family,typed(ts),typed(close_ts)]. Exact acceptedstrings and {'kind':'int','value':hex(n)} clockobjects; no alternatives/objectaliases/encodedstringtuplehash. Computed from reproducedcoveredrows, neveraccepted from publicdocument. Every membership derives onlyexplicitclosemembers; completecoverage checked beforecanonicalization. Duplicate subjectkeys cannot be masked by revisions.

Inspection payload EXACT keys: contract_version,rule_id,access_id,action,access_status,actor,declared_at_ts,note,input_id,start_ts,end_ts,source_watermark,members,candidate_id,selection_id. Versions research-inspection-v1/phase18-temporal-v1. access_id serveruuid4.hex32lowerhex. action validation/oos/external. access_status first_access/repeat_access/external_declaration. Allnumbers (bounds, watermark, nonnullclaimedtime) exacttypedint; strings/null unchanged. Forvalidation candidate_id required, selection_id null; foroos selection_id required,candidate_id null; forexternal bothnull, note required and claimedtime optional. Softwareactions note and declaredtime null. Actorvalidnonemptytext. No wirecaller access_status/UUID/watermark/members field accepted; server derivesall.

Repeat scope: prior softwareinspection with sameaction and (validation: candidate_id,input_id,start,end; oos:selection_id). Actor DOESNOT reset scope. First if none earliercommittedmatching, repeatotherwise; everycall stilldistinctuuid/event. external alwaysexternal_declaration, never claimsindependentaccess. These labels describe loggedaccess only, not independentstatisticalevaluation/reproductionresult. No actualresultpublished in k.

Lifecycle replay on sameconnection: parseexactcanonicalJSON with duplicatekey/noncanonicaltypedhex rejection; payloadhash/kind and indexedcolumns match; exactpayloadkeysets; UUIDformat/conditionalnulls/actions/status checked. Selection replay replayscandidate/inputevents, recomputesallbindings/memberships/fullcanonicalpayload and requiresbyteequality; inspection replay replaysreferences and recomputessubjectmembership. Require referencedsourceevents seq<=persistedsource_watermark forinspection; selectedselection lifecycle seq<inspectionseq. Recomputefirst/repeatstatus against ONLY earlierinspectionseq events; no self/later/cyclicreferences. Selectionvalidationproof/contamination reconstructed against ONLY earlierlifecycleevents, so laterinspectioncannot invalidate anoriginallegitimatefreeze. Never truststoredmembers withoutreproduction or indexedrevision withoutdecodedagreement. Integrityfailure exactexisting `stored research event failed integrity validation`; no hash/UUID authenticatesmaliciousSQLiteowner.

Freeze idempotence: validatepublicdocument and deriveexactbindings/memberships via immutablecandidate/source replay; lookup sameexperiment/hypothesis/revision. If originalpayload exactlyequalsnewderivedpayload, replayoriginalagainstits ownhistoricalseq andreturnoriginalBEFORE applying currentinspection checks. Changedpayload under samerevision raisesrevisionconflict. NEWrevision applies fullcurrentbarrier beforeinsert. This prevents genuineexactrecapture beingblocked bylaterinspection while forbidding after-the-factchangedselection. No idempotence shortcut trusting callerhash or skippingoriginalintegrity.

## Contamination subject and access semantics

Capturedinputs syntheticBTCcontinuousdailyonly. Subjectkey explicitly (venue,symbol,timeframe,source_family,ts,close_ts), source_family='controlled-fixture:controlled-daily-linear-v1'. Intkeys exact. Ignore snapshotID, recipehash, revisionID, payloadprice andsourceanchor differences for contaminationmatching WITHINthisfamily: sharedrealbar-clockobservations across alternate syntheticrecipes are conservativelytreatedpreviouslyinspected. This restricts, never certifiesunseenmarkettruth. No unknownreal-sourcemapping/default accepted. Membership is finite actualcompleteclosememberkeys, not merelyintervalhash. A renamednewrevisionorpricechange cannot reset sameclocks' inspection. Inspect allledgeractors/experiments: newexperimentdoesnoterase sameholdoutaccess.

Validationaccess: replaycandidateexisting, inputfixturefullcoverage; candidateISend<=validationstart; initialcandidate must predate every earlierexternal/oosinspection of requestedvalidationkeys (candidate.seq<=watermark), else reject. Do not prohibit repeatedvalidationaccess for samefrozencandidate; softwarevalidationrecord sourcewatermarkprovesexistingfreeze. Requestedvalidation keys must not overlap ANYregisteredselectionOOSkeys, and must not overlap anyprioroos/externalinspectionkeys: OOS cannot silentlybecomevalidation in this bounded access path. SC15 remains supported: a NEWcandidate_revision may explicitly declare previouslyinspectedOOSobservations as its NEW IS range/input (j capture permits this), retainingparentlineage, and then freeze NEWfinalselection with a genuinelyuninspected disjointholdout. Priorresults remainunchanged and oldholdout is nowdeclareddevelopmentdata, neverindependentfinalevidence. This reclassification doesnot require silentvalidationreuse or eraseledgerhistory; commonvalidation ifused must satisfy this boundedgate. A newhash/revision cannot reuseoldholdout as finalOOS.

OOSaccess: replayvalidselection, resolve exactholdoutinput/range/memberkeys, append inspection THENreturnONLYthoseobservations. Firstaccessfrozenbeforeinspection by transactionexistence. Repeatedsame selection permits reproduction/inspection, distinctevents; no independenttrialclaim. Newselection afteranysuchaccessrejects same/overlappingholdout. Access is not executionreservation/result and cannot claimcompletedOOS.

Externalinspection: validatescapturesource/fullcoverage, actor+note explicitvalidtext, declared_at integerexcludingboolorNone. Appends regardlesswhetherselectionexists, never blocksrecording truthfulcontamination. Mayrecordearlierclaimedtime; applications cannot proveoutsidebehavior. Does not returnobservations. Existing frozenresults/selections unaffected; laterselectionnewunseenholdoutrequired. Unknownunreportedinspection/predictablesyntheticprices remainunverified.

## Exact validation order/messages

OneownERRORquant.data.research_store and identicalValueError; acceptedsource/coverageerrors propagateonce. No actor/note/payload leakage. Reuseexistingintegritydecoder/error forstoredpayloads.
Selection order: exactkeys; version/ruletokens; textfields experiment/hypothesis/revision/selected/input/criteria; consideredcontainer/IDs/duplicates; validationNoneorfields/text/int/order; OOSint/order; BEGINIMMEDIATE consideredreplay/group/trials/selectedmembership; derivecanonicalbindings and samecontentrevisionidempotence/conflict beforecurrentinspectionchecks; immutable source coverage is performed while deriving bindings/memberships before revision comparison; for NEW revisions only, chronology; criteria-change lineage; validationaccessproof; selection/OOSmembershipdisjoint; priorholdoutinspection; append.
Messagesfixed:
`selection must contain exactly the declared fields`; `<field> must be <token>`; `<field> must be a nonempty UTF-8 string without NUL`; `considered_candidate_ids must be a nonempty list or tuple of unique candidate IDs`; `validation must be null or contain exactly input_id, start_ts, and end_ts`; `<field> must be an integer excluding bool`; `<range>.start_ts must be less than <range>.end_ts`; `<field> must align with the declared daily grid`; `selection revision already has different frozen content`; `research candidate event does not exist`; `research input event does not exist`; `considered candidates must match experiment and hypothesis`; `considered candidates must enumerate the declared trial budget`; `selected candidate must be considered`; `research ranges must be chronological and nonoverlapping`; `validation access must precede final selection for every considered candidate`; `validation was inspected before candidate freeze`; `validation absence conflicts with recorded validation access`; `selection data must not overlap final holdout observations`; `final holdout observations were already inspected`; `validation observations overlap a final holdout or OOS inspection`; `research selection event does not exist`; `changed selection criteria require a new candidate revision with prior selection lineage`.
Accessvalidationparameterchecks candidate/input/actor text,start/endtypes/order thenrefs/coverage/chronology/overlap/watermark; OOS selection/actor textthenrefs; external input/actor/note textthenbounds/declaredtime types/orderthenrefs/coverage. Coveragemessagesexacthelper; no redundantexhaustivematrices. Missingorcorruptrecordnotempty/unverifiedfallback.

## Focused actual DB tests and acceptance

tmp_pathSQLiteactualfreeze thenvalidationaccess, optionalvalidationselection, finalfreeze thenoosaccess; exactreturnedmembership noIS/laterrows; parameters/code remainboundcandidateids; explicitcount/trialmismatch/selectednotconsidered/validationabsencefailure. Independentcanonicalbytes/IDs, typedlargeclocks, samecontentidempotence vschangedrevisionfailure. Backdatedwallclock/manualdeclaredtime cannotoverridewatermark/ledgerordering. Inspectionbeforeselectionreject, legitimateexactrerunaccesspreserveddistinct, newcandidate/newexperiment/newsnapshot/changedrecipe overlappingkeys cannotresetcontamination; disjointunseenkeys allownewselection. Candidatecapturedaftermanualinspectionfailsvalidationwatermark, candidatealreadyfrozenpermitsdeclareddevelopmentvalidation only ifnotOOScontaminated. Fakecorruptsource/lifecycle/indexedcolumn/subjectmappingfailsbeforedatareturn. UPDATE/DELETEtriggers reject.
TwoactualSQLitecontenders freezevsmanualinspection deterministicbarrier: selectionfirst commitspermitsfreeze theninspection; inspectionfirst preventsnewfreeze; neverbothsuccessfulcontradictoryclaim. Injectinspectioninsert/commitfailure -> noobservationsreturned,nororphanselection; no timingbasedassertions/retrymask. Tests previoussource/capturecontract unchanged, no engine/UI/deps/networkrequired. Eachnewfunctionmeaningfulpublicpathcoverage; do notduplicate acceptedtype/calendar/helpermatrices.

Rootexistingvenv exact .venv/bin/python -m ruff check .; .venv/bin/python -m mypy --strict backend/src; .venv/bin/python -m pytest backend/tests -q; git diff --check; git status --short. Onefullsuite doer/freshreviewer exceptjustifiednewfailure/correction; enablednetworkdefault unchanged,max5loops, completefailure/outputretained. One terminalcommit feat(data): enforce transactional research observation barriers (Phase 18.2k). SeparateindependentacceptanceSTATE; authorizedPRchecks/merge thenfreshnextreadiness. No automatic later READY or completion.

Claimlimit: actualstoregateway selection/observationmechanics only, not integratedAPI/worker/CLIrun, completedfinalevaluation, historicalsourceauthenticity, undetectedexternalbehavior/unseenmarkettruth/statisticalindependence. Next boundedextension evaluationreservations+immutablecompletion/result-accessinspection; then actualruntimecandidate/fixturebinding and API/CLI/worker integration. Namedgaps18.3 andexplicitwindows18.4 stillfollow acceptedgates. NoPhase18completionfromthisstorealone.


Readiness changed STATE only. No Python files changed; pytest/ruff/mypy were not
re-run under WORKFLOW §5. No implementation, suites, installs, push, merge or
workers. Current task18.2k READY; next_task null; last_completed_task18.2j;
human_transition_required false; remaining18.2, 18.3 and18.4 NOT_STARTED;
Phase18 IN_PROGRESS. No whole-phase claim or automatic phase crossing.

### 18.2l independent readiness contract — 2026-10-04 Asia/Manila

Independent readiness opens ONLY **18.2l READY**. Verified clean dedicated
branch `phase18/18.2l-evaluation-reservations`, baseline HEAD and `origin/main`
`a88b9b5a05f1aac8e5723e60beb9948a226f5bc7`. Independent live
`git ls-remote origin refs/heads/main` under the default sandbox returned that
exact SHA (exit 0); point-in-time evidence only. PR14 is integrated by a normal
merge. `git diff --quiet 4e152be7b6683058e61974e618c46b82581abd10 HEAD`
exit 0 proves the exact independently accepted tree. Accepted implementation
`b47ada07407c656063255be738e85b1b1baa135d` and reviewer completion
`4e152be7b6683058e61974e618c46b82581abd10` are both ancestors of HEAD
(independent ancestry checks exit 0). Remote identity remains
`https://github.com/colossalshub/colossal_quant.git`; terminal author identity
Michael Gamet / michaelg.devs@gmail.com. Coordinator reports PR14's three GitHub
checks successful and no open review/thread items; this readiness independently
verifies merged tree/lineage, not a new GitHub check run.

Read AGENTS, full STATE/WORKFLOW/REVIEWER/INCIDENTS, PROJECT §§2, 4.1, 4.5, 5,
6.0, Phases14–18, completion and §§7–8; full confirmed Phase18 specification,
applicable project/backend rules, existing store/tests and fixture/input contracts.
The following exact bounded contract is preserved from the proposal in the
repository; implementation has no dependency on disposable scratch notes.
The existing private `_access` supports same-connection inspection append,
while the new reservation transaction must commit both ledgers before release.
No unfamiliar third-party call or dependency is introduced; stdlib SQLite,
UUID, JSON, hash and clock patterns are already used, so no new probe is needed.
Delegated trustworthy routine decisions authorize this conservative split.
The k completion/readiness, post-probe approval and permanent rules remain
byte-preserved; no archive maintenance occurs in this readiness.

## Decision and practical sequence

Implement one useful store operation family now: atomically reserve one immutable candidate/input/range for one run and log its observation release. It is the missing durable bridge from frozen research evidence to execution. Do not also design a generic result JSON tree or accept a client `eligible`, `success`, `actual_code`, `residual`, or environment label as runtime proof. Store reservation, runtime receipt production, and guarded result access have different evidence sources; bundling all into this already 1,347-line store would hide a large new contract.

After accepted l, the next store task adds immutable success/failure receipts with a narrowly specified trusted runtime writer and guarded result access; the next runtime task connects those operations to the accepted research adapter, checking actual git/code/parameters/input/seed/environment and extracting actual results/residual evidence. Those tasks may be reordered if receipt design needs the runtime producer first; each is a useful operation plus its actual tests, not a speculative pure helper family. Then add RunRecord/admission transport and orchestrator/worker/CLI integration in the fewest workflow-compliant file-plus-test tasks. Finish 18.3 named explicit gaps and 18.4 enumerated sequence/window identities/results only after their gates. Never claim Phase18 complete from store acceptance. No optimizer, aggregate returns, unknown API call, calendar repair, global gap/warmup/window default or new dependency.

## Deliverables and interfaces

Only `backend/src/quant/data/research_store.py` and `backend/tests/data/test_research_store.py`. Existing source/candidate capture, selection/inspection schemas, payloads, errors and contracts remain unchanged. Preserve the scoped ContextVar replay normalization and source-error propagation once.

Frozen slots dataclasses:

* `ResearchEvaluationReservation(seq:int,event_id:str,evaluation_id:str,run_id:str,recorded_at_ts:int,canonical_bytes:bytes)`.
* `ResearchReservedObservations(reservation:ResearchEvaluationReservation,inspection:ResearchLifecycleEvent,observations:tuple[ResearchObservation,...])`.

Direct construction is unvalidated. Both records are internal and have no eligibility/success flag. Functions:

```
reserve_validation_evaluation(db_path:Path, *, run_id:str,candidate_id:str,input_id:str,start_ts:int,end_ts:int,actor:str)->ResearchReservedObservations
reserve_oos_evaluation(db_path:Path, *, run_id:str,selection_id:str,actor:str)->ResearchReservedObservations
```

OOS candidate, input and bounds come exclusively from the replayed frozen selection; no duplicate overrides. Validation uses the explicit frozen candidate and covered development range under k's exact validation gate. Exploration/ordinary runs are outside these operations. A reservation is not completed execution and does not declare warmup, dependencies or gap compliance. The later execution identity must bind explicitly supplied warmup/dependency/gap evidence together with actual runtime identities; reservation binding below is deliberately only the immutable candidate/stage/input binding.

Every accepted call creates a new server UUID4 hex `evaluation_id`. `run_id` is explicit valid nonempty UTF-8 text, not necessarily a UUID; it binds the application's run, not proof that meta_runs or a worker exists. Each run_id can reserve exactly once globally in this ledger. A duplicate run_id rejects, even for identical content; a retry/exact rerun uses a new run_id and evaluation_id, preserving the original reservation/outcome. No idempotent release shortcut or public unlogged reservation/raw source/lifecycle getter. Later workers must arrange a new run on retry rather than treat the prior failed/reserved run as independent evidence.

## Transaction and storage

Add private `research_evaluation_reservations_v1` via existing `_connection`, so init and every read/mutation path initialize schema. Columns exactly `seq INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT UNIQUE NOT NULL,evaluation_id TEXT UNIQUE NOT NULL,run_id TEXT UNIQUE NOT NULL,recorded_at_ts INTEGER NOT NULL,payload BLOB NOT NULL`. UPDATE/DELETE triggers use existing append-only error `research events are append-only`. No alteration of k's restrictive selection/inspection CHECK or capture table. A future separate completion table references a reservation; do not scaffold unused kinds/columns now.

Use one `_connection` and `BEGIN IMMEDIATE`: replay source/lifecycle and reservation ledgers; reject duplicate run_id; resolve immutable candidate/source/selection and validate existing k gates/coverage; call the PRIVATE same-connection inspection operation; append reservation referring to that new inspection; commit both before returning any observation/record. Never call public `access_*` inside the transaction (nested connection/locking/race). On insert/commit/error roll back both ledger changes and return no observations. Read-only historical replay itself appends no access or reservation; connection initialization does not convert replay into inspection.

The existing inspection logs all observation release and is sufficient contamination evidence even when the caller never executes or crashes. Every reservation gets a distinct inspection event with k's actor-independent first/repeat ACCESS status. Do not add an `independent` or `reproduced` evaluation status inferred from equality. Exact repeats are comparisons awaiting actual outcomes. New selections still require unseen holdouts under k; candidate/code/data changes never erase contamination.

## Canonical payload and identities

Reservation payload EXACT keys:

`contract_version,rule_id,evaluation_id,run_id,actor,stage,candidate_id,candidate_payload,selection_id,input_id,input_snapshot_id,membership,inspection_id,source_watermark,lifecycle_watermark,binding_id`.

Tokens `research-evaluation-reservation-v1`, `phase18-temporal-v1`; stage `validation`/`oos`. UUID lowercase hex32. candidate_payload is parsed exact existing immutable canonical candidate document (its numbers already typed); selected candidate for OOS. selection_id nonnull only OOS. input_id is capture event identity; input_snapshot_id is the actual reproduced `ResearchInputSnapshot.snapshot_id`, never caller hash. membership is EXACT existing covered membership shape `{input_id,start_ts,end_ts,members}` with only actual requested half-open close members and k's subject keys. No full raw input batch/recipe in reservation metadata. Actual observations returned are only that membership, not IS/later rows. Do not expose canonical records blindly through a future API.

inspection_id refers to the inspection appended in this transaction. source_watermark = MAX(capture seq) and MUST exactly equal the linked inspection's source_watermark, since no capture is appended in this transaction; lifecycle_watermark = linked inspection.seq = MAX(lifecycle seq) after that inspection. Do not compare seq across tables; inspect source refs against source watermark and lifecycle refs against lifecycle watermark. recorded_at_ts is server wall clock and has no ordering authority.

binding_id = sha256 identity of canonical EXACT projection `{contract_version,rule_id,stage,candidate_id,candidate_payload,selection_id,input_id,input_snapshot_id,membership}`. Use reservation contract token here as well. It excludes actor/run/evaluation/access IDs and watermarks, so exact same candidate/stage/input binding remains comparable across reruns. Changed raw fixture values, recipe, candidate parameters/code/seed/rules or frozen selection changes binding/evaluation identity (unsupported rules reject). Every call has distinct evaluation_id and event_id even when binding_id matches. This binding is not yet an actual runtime/environment identity or authentication.

Canonical encoding exactly accepted sorted compact UTF-8 JSON/no BOM/newline, all numeric positions typed `{kind:'int',value:hex(n)}` or existing float.hex objects, never bare JSON numbers. Bounds/watermarks typed ints excluding bool. Existing parameter decimal strings retain admitted spelling. event_id = sha256 prefix + digest of full canonical payload. Reject duplicate/noncanonical JSON/typed hex on replay rather than silently normalizing.

## Replay and historical ordering

Private same-connection replay ordered by reservation seq. Reuse source and lifecycle integrity replay first, then validate exact key sets, tokens, UUID/text/stage/null shapes, canonical bytes/digest and every indexed column. Reproduce candidate/source and snapshot identity/complete membership; require candidate/input captured at or before source_watermark, selection and linked inspection within lifecycle_watermark. Linked inspection MUST match stage, actor, candidate_id (validation) or selection_id (OOS), input and bounds/members exactly. For OOS derive candidate from that selection and require it before inspection. source_watermark MUST exactly equal the linked inspection's source_watermark; lifecycle_watermark MUST equal linked inspection.seq. Each reservation links its own distinct software inspection (validation/oos, never external): forbid inspection_id reuse across reservations and require linked inspection sequences strictly increasing in reservation seq order. Unrelated lifecycle events may intervene; compare linked lifecycle sequences only to each other, never to reservation/source seq. These constraints reproduce serialized atomic call ordering without relying on wall time. Recompute binding_id and full expected payload byte equality, not hash-only comparison.

Historical replay validates inspection/selection against their earlier lifecycle prefixes as k already does. Later inspections/new candidate/selection revisions do not invalidate old reservations. Watermark may be below today's maximum, never above it. Replay cannot authenticate a malicious database owner. Validate evaluation_id/run_id uniqueness as well as SQLite constraints; missing/corrupt referenced records fail before release. No future completion facts reconstructed from a reservation.

## Error order and fixed messages

Public argument validation before opening transaction: validation run_id,candidate_id,input_id,actor text in that order, then k validation bound types/order; OOS run_id,selection_id,actor text. Existing `<field> must be a nonempty UTF-8 string without NUL` and bound messages retained. Then BEGIN/replay all ledgers, duplicate run_id, reference existence, source reproduction/coverage and k chronology/contamination gates, append inspection, derive binding/append reservation, commit.

New duplicate error exactly `run already has a research evaluation reservation`. Reference errors remain k's `research candidate event does not exist`, `research input event does not exist`, `research selection event does not exist`. Persistent reservation corruption uses exactly existing `stored research event failed integrity validation`, one own ERROR + ValueError; preserve source/coverage errors once and original SQLite exceptions. No input/actor/note/payload leakage. Scope integrity normalization with finally reset, preserving concurrent isolation and existing source decode behavior.

## Meaningful tests and acceptance

Actual tmp_path SQLite: accepted validation reservation before final selection proves logged validation access for each considered trial; OOS reservation follows selection and returns exact held-out rows and selected frozen candidate binding; no IS/later leak. Same exact rerun/new run preserves same binding_id but distinct evaluation/inspection/event IDs; actors do not reset repeat access. Duplicate run rejects before inserting either new event, including competing two-connection calls; changed code/parameters/input/selection yields changed binding with preserved old reservation and contamination. Missing/wrong reference and covered-range errors unchanged. Independent canonical bytes/binding hash expected in test, large clocks typed exactly. Reopen/replay old reservation after later inspection/selection remains valid without new writes.

Corrupt payload/hash/indexed run/evaluation IDs, snapshot_id, candidate_binding, membership, linked inspection/actor/stage, watermark mismatch/future references, reused inspection_id, reversed linked-inspection order and canonical typed values fail before data release; legitimate unrelated intervening lifecycle events remain valid. Do not duplicate exhaustive accepted source/type/calendar matrices. UPDATE/DELETE triggers reject. Inject reservation insert failure and commit failure: no orphan inspection/reservation/no data return, original exception preserved. Deterministic actual SQLite contenders with explicit barrier/events (no timing assertions/retry masking) prove duplicate run serialization; existing freeze-versus-inspection coverage remains green. Every new public operation has meaningful end-to-end path coverage; no mocked-self verification.

From repo root, exact existing interpreter:

1. `.venv/bin/python -m ruff check .`
2. `.venv/bin/python -m mypy --strict backend/src`
3. `.venv/bin/python -m pytest backend/tests -q`
4. `git diff --check`
5. `git status --short`

One full suite per doer/fresh independent reviewer unless a correction/failure justifies another. Preserve full command output/failures; <=5 debugging loops; enabled network/default sandbox/proxy/TLS unchanged. Only declared two files, no STATE/protected docs/pyproject/UI/data edits. Terminal commit `feat(data): reserve run-bound research evaluations atomically (Phase 18.2l)`. Report exact SHA/files/tests/output/deviations/limitations. Independent acceptance then separate STATE docs commit, authorized PR checks/integration, fresh next readiness; no automatic later READY.

## Claim limits and next receipt gate

This task establishes durable reservation + inspection before release, not evaluation completion, worker uniqueness, executable code authenticity, outside-inspection certification, real historical publication history, realistic fills, untouched synthetic truth, or statistical independence. Candidate git40 SHA remains a caller assertion until runtime compares actual checkout/code; synthetic fixture supports software mechanics only.

Next receipt/result readiness must specify immutable one-terminal-outcome-per-evaluation storage (failure retained), actual runtime-produced exact input/env/code/seed/effective execution settings and residual-position/last-eligible-price evidence, and successful/failed meaning distinct from eligible/unverified guarantees. A public result accessor must append the existing OOS inspection on the SAME connection/transaction BEFORE returning any result/artifact/derived metric; failures roll back/no release. No result metadata list, raw getter, download or legacy API path may bypass that gateway once integrated. Internal completion API is for the bound runtime writer, never client attestations treated as actual proof. Narrow unsupported guarantees remain unverified or fail explicitly; do not downgrade designated research execution to ordinary execution.

Readiness changes STATE only. No Python files changed; pytest/ruff/mypy were not
re-run under WORKFLOW §5. Whole documentation diff and status checked; no
implementation, suites, installs, workers, push, PR or merge performed here.
Current task18.2l READY; next_task null; last_completed_task18.2k;
human_transition_required false; remaining18.2, 18.3 and18.4 NOT_STARTED;
Phase18 IN_PROGRESS. No accepted runtime, result or historical-validity claim.

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
