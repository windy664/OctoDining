# Developing this OctoSense app

> **Any coding agent, or none.** These instructions work the same for Codex, Claude Code, Cursor, Gemini CLI, GitHub Copilot or a person at a terminal: every step is a shell command or a file edit, and nothing here needs a particular agent, model or vendor. `AGENTS.md` is the one source of truth; `CLAUDE.md` and `GEMINI.md` only import it for agents that look for those names.

This repository is one OctoSense script app. `bundle/` is the app and the only
thing submitted to the App Hub; everything else stays outside it.

Follow the harness, and do not invent requirements or APIs:

- How to build, run and test: [QUICKSTART](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/QUICKSTART.md)
- The language and every API an app may use: [SCRIPT-API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/SCRIPT-API.md)
- Capabilities: [CAPABILITIES](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/CAPABILITIES.md)
- Publishing, step by step, with the human checkpoints: [PUBLISHING](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/docs/PUBLISHING.md)

The loop, with `OCTO=<path to OctoScript-App-Design-Flow>/tools/octo` (the CLI
lives in the harness repository, not here), run from this directory: edit
`scripts/main.splash.in` → `python3 scripts/build-octos-bundle.py`
→ `python3 scripts/dev_bundle.py --output .local-state/preview-bundle`
→ `$OCTO run .local-state/preview-bundle --port 8141 --detach` → drive it
(`/click`, `/t`, `/snap`) and `$OCTO shot 8141 out.png` → `curl -s 127.0.0.1:8141/quit`
→ `$OCTO check .local-state/preview-bundle`. The tracked `bundle/` is a signed
release; card-host tests use an unsigned local copy. Any source or bundle edit
requires a new release commit, stamp and publisher signature.

Rules:

- Ask only for capabilities a screen uses; declare every `https://` host in
  `network.hosts`; never `http://`.
- Never collect a password, PIN or code; accounts go through a host service.
- Screenshots are real captures you looked at. Never a dummy.
- Restamp after every edit (`tools/octo check` does it). After signing, any
  edit needs a new stamp and signature.
- Keys, `.local-state/`, `build/` and review packets never enter `bundle/` or git.
- Stop at human steps: publisher key, publisher details, platform claims, submission.

## OctoDining project direction (2026-10-03)

- Read `README.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` and
  `docs/CONTEST_READINESS.md` for the current direction and actual status.
- Prioritize an OctoScript app hosted by OctoSense Shell, using its system octos
  service. Basic selection/planning has passed card-host checks; validate Shell
  authorization and real Agent requests before claiming that works.
  Rinx is an optional host for chat sharing, not a prerequisite for the personal
  dining task. Do not confuse `tools/octo`, `card-host`, octos and OctoSense.
- Continue in this order: basic functionality (now implemented), runtime Agent
  validation, then UI polish. Record host blockers without overstating evidence.
- Preserve the original menu data, A1–A6 tiers, weekly planner and design assets.
  HTML and Rust/egui remain reference implementations; do not replace the
  competition app with an unrelated GUI framework.
- Treat `scripts/main.splash.in` as the source and `bundle/main.splash` as generated
  output. Rebuild and check after every app or manifest edit.
- Distinguish source presence, runtime verification and planned work. A model
  response, card-host run or Hub check does not prove the Shell Agent task is
  complete. Report tested commits and remaining limitations. Current hidden
  window capture returns 404; do not claim screenshot review until fixed.
- The 1,497 menu entries are snapshots, not live price, stock, nutrition or
  allergy data. Never invent unsupported facts. Confirmed plans are not orders.
- Historical notes in `docs/CONTINUATION.md` and `docs/HANDOFF-2026-10-03.md`
  are context only. Current task instructions take precedence.
- Do not run the historical `start-demo.sh` as the default launcher. It controls
  Rinx processes. `scripts/preview.sh` runs a local unsigned copy and stops a
  previous preview on port 8141; set `OCTO_CLI` if the harness is elsewhere.
