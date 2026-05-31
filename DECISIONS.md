# Decisions Log: Kotlin-to-Python Migration

## 2026-05-31

### Decision 1: Start with additive Python scaffolding only
- **Decision:** Begin migration by adding a new `kotwords_py/` package without modifying existing Kotlin production paths.
- **Reasoning:** This keeps risk low, allows incremental parity work, and preserves current release behavior.
- **Consequence:** Python code is not yet wired into build/release automation.

### Decision 2: Port `Puzzleable`, `Puzzle`, and `Crossword` first
- **Decision:** Implement first-pass parity for foundational model/conversion behavior from Kotlin (`Puzzleable`, `Puzzle`, `Crossword`).
- **Reasoning:** These are central primitives used by later format, CLI, and web phases.
- **Consequence:** Current Python implementation intentionally covers only core semantics and not full format support.

### Decision 3: Use Python stdlib for the first pass
- **Decision:** Use `dataclasses`, `Enum`, and `asyncio` instead of adding new dependencies immediately.
- **Reasoning:** Minimizes setup overhead and keeps early migration changes small and reviewable.
- **Consequence:** Validation/serialization helpers may later migrate to third-party libraries when broader parity requires them.

### Decision 4: Maintain a parity-first progress ledger
- **Decision:** Track migration state in `PROGRESS.md` using the section outline of `PLAN.md`.
- **Reasoning:** Ensures traceability between long-term plan and implementation cadence.
- **Consequence:** Progress updates must be maintained alongside each implementation increment.
