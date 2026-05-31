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

### Decision 5: Add `DelegatingPuzzleable` before format-engine ports
- **Decision:** Implement Python `DelegatingPuzzleable` now, even before concrete format converters.
- **Reasoning:** Composite adapters are already a core pattern in Kotlin and this keeps Python architecture aligned early.
- **Consequence:** Future parser/adapter ports can reuse a tested delegation primitive instead of recreating ad hoc forwarding logic.

### Decision 6: Add Python async caching contract tests in-repo
- **Decision:** Add `unittest`-based async tests for `Puzzleable.as_puzzle()` and `DelegatingPuzzleable`.
- **Reasoning:** Caching/delegation behavior is foundational and can regress silently without direct tests.
- **Consequence:** Python scaffold work now has a direct parity guardrail while remaining dependency-free.

### Decision 7: Introduce ZIP abstraction before parser ports
- **Decision:** Add Python `Zip` helpers and `InvalidZipError` with Kotlin-matching unzip failure messages.
- **Reasoning:** Multiple future formats (JPZ/RGZ and compressed payload adapters) depend on predictable ZIP semantics.
- **Consequence:** Parser ports can share one tested unzip path and consistent exception mapping from the start.

### Decision 8: Prioritize spiral-family model parity next
- **Decision:** Port `Spiral`, `TwoTone`, and `JellyRoll` next, with a shared Python spiral-grid helper.
- **Reasoning:** These model types share traversal/numbering behavior and provide broad parity value from one reusable primitive.
- **Consequence:** Future spiral-derived model ports can reuse `spiral_grid` rather than re-implementing coordinate and border logic.

### Decision 9: Validate scaffold parity with focused variant tests
- **Decision:** Add dedicated Python tests for spiral-family clue grouping and word-id generation.
- **Reasoning:** These models have non-trivial numbering/grouping behavior that can silently regress without direct tests.
- **Consequence:** The migration now has stronger parity guardrails while remaining dependency-free and fast to run.

### Decision 10: Port row-wrapping and overlap-driven variants next
- **Decision:** Port `AroundTheBend` and `SnakeCharmer` into the Python scaffold before larger grid-rendering variants.
- **Reasoning:** Both models add distinct parity behaviors (row wrapping and coordinate overlap conflict checks) while staying independent of PDF/web dependencies.
- **Consequence:** Additional non-rectangular and multi-number cell semantics are now covered earlier in migration phases.

### Decision 11: Add fixture-inspired Python contract tests for new variants
- **Decision:** Add focused Python tests validating AroundTheBend word wrapping and SnakeCharmer overlap/numbering behavior.
- **Reasoning:** These variants rely on subtle coordinate transforms that are easy to break without direct assertions.
- **Consequence:** Future parser/model ports can reuse these tests as parity guardrails without external dependencies.

### Decision 12: Add coded and crosswordle parity before format engines
- **Decision:** Port `Coded` and `Crosswordle` model builders into the Python scaffold now.
- **Reasoning:** They add distinct grid-state behavior (substitution hints and wordle-style match coloring) while remaining isolated from format-writer dependencies.
- **Consequence:** The migration now covers additional model semantics and can validate more variant-specific behavior without waiting on parser ports.

### Decision 13: Add downs-only clue transformation helper parity
- **Decision:** Implement Python `DownsOnly` with Kotlin-aligned clue-direction heuristic and clue-clearing behavior.
- **Reasoning:** This utility is a standalone transformation used on already-built puzzles and is inexpensive to port with strong parity value.
- **Consequence:** Python model flows can now reproduce down-clues-only generation semantics and include direct guardrail tests for conversion preconditions.

### Decision 14: Port HelterSkelter vector resolution before format engines
- **Decision:** Implement Python `HelterSkelter` with both explicit `AnswerVector` support and Kotlin-style auto-vector inference.
- **Reasoning:** It adds a distinct directional path-finding model that increases parity coverage while staying independent of parser/PDF/web dependencies.
- **Consequence:** Python scaffolding now includes validated vector ambiguity/not-found guardrails and supports edge-extension semantics for future variant and adapter ports.

### Decision 15: Port patch-partition grid semantics before format engines
- **Decision:** Implement Python `Patchwork` model conversion now, including row clues, piece clues, and per-cell border generation between pieces.
- **Reasoning:** Patchwork introduces unique piece-boundary semantics and clue/word mapping that can be ported and validated without parser or rendering dependencies.
- **Consequence:** Python parity coverage now includes partitioned-grid behavior and optional unlabeled-piece output logic needed by future format exports.
