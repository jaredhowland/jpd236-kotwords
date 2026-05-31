# PROGRESS: Kotlin-to-Python Migration

This document tracks implementation progress against `/tmp/workspace/jaredhowland/jpd236-kotwords/PLAN.md`.

## 0) Plan status
- In progress.
- This migration is currently parity-first and avoids feature expansion.

## 1) Objective
- Status: In progress.
- Initial Python scaffold has been created to start porting core models.
- Added foundational delegation parity (`DelegatingPuzzleable`) and async cache contract tests.

## 2) Scope and parity targets
- Status: In progress.
- Started with core model scaffolding (`kotwords_py/model`) and conversion abstraction (`kotwords_py/formats`).
- Added shared ZIP abstraction parity for compressed format support (`kotwords_py/formats/zip_file.py`).
- Added spiral-family model parity scaffolding (`Spiral`, `TwoTone`, `JellyRoll`) with shared traversal helpers (`kotwords_py/model/spiral_grid.py`).
- Added row/coordinate-variant parity scaffolding (`AroundTheBend`, `SnakeCharmer`) for wrapped rows and overlapping path models.
- Added coded-grid and crosswordle variant parity scaffolding (`Coded`, `Crosswordle`) and downs-only clue-clearing parity helper (`DownsOnly`).
- Format engines, CLI, and web parity are not implemented yet.

## 3) Baseline inventory (must be frozen before migration)
- Status: In progress.
- Used current Kotlin `Puzzle`, `Crossword`, and `Puzzleable` as first parity references.
- Full API/fixture inventory freeze remains pending.

## 4) Target Python architecture
- Status: In progress.
- Added:
  - `kotwords_py/`
  - `kotwords_py/model/`
  - `kotwords_py/formats/`
- Remaining architecture folders are pending.

## 5) Dependency mapping plan
- Status: In progress.
- Initial implementation uses Python stdlib (`dataclasses`, `enum`, `asyncio`) only.
- Third-party dependency decisions deferred until more format engines are ported.

## 6) Migration order (phased, risk-first)
### Phase A: Foundation and shared types
- Status: Started.
- Implemented initial Python model primitives for `Puzzle` and `Crossword` flows.
- Implemented Python spiral-based model converters (`Spiral`, `TwoTone`, `JellyRoll`) and supporting spiral-grid traversal utilities.
- Implemented Python `AroundTheBend` and `SnakeCharmer` model converters with Kotlin-aligned numbering and overlap validation behavior.
- Implemented Python `Coded` and `Crosswordle` converters, including given-letter hints, crosswordle cell-state coloring, and synthetic answer-row numbering semantics.
- Added Python downs-only clue-clearing helper parity (`DownsOnly`) with grid-stat heuristic matching Kotlin selection rules.
- Added Python async contract tests for base conversion caching behavior.

### Phase B: Platform abstraction equivalents
- Status: Started (partial).
- Added `Puzzleable` abstraction with async cached `as_puzzle()` behavior.
- Added `DelegatingPuzzleable` abstraction parity for composed puzzle containers.
- Added Python `Zip.zip()` / `Zip.unzip()` and `InvalidZipError` behavior parity.
- Added reusable Python spiral coordinate generation for parity across spiral-derived models.
- Added Python parity implementations for row-wrapping (`AroundTheBend`) and overlap-mapped (`SnakeCharmer`) model generation.
- Added Python parity implementations for coded substitutions (`Coded`), crosswordle clue coloring/numbering (`Crosswordle`), and clue-direction reduction (`DownsOnly`).

### Phase C: Core format engines
- Status: Not started.

### Phase D: PDF pipeline
- Status: Not started.

### Phase E: CLI and web parity
- Status: Not started.

### Phase F: Packaging and release
- Status: Not started.

### Phase G: Cutover and deprecation
- Status: Not started.

## 7) Testing and verification strategy
- Status: In progress.
- Repository baseline check (`./gradlew check`) fails in this environment due to blocked Kotlin/Native download host.
- Existing JVM/JS validation remains the near-term verification path for non-native changes.
- Added Python scaffold validation via `python -m unittest discover -s tests -p "test_*.py"`.

## 8) Edge cases that must be explicitly covered
- Status: Started.
- Added ZIP edge-case tests for invalid archives and no-file-entry archives.
- Added spiral-variant model tests validating clue grouping and word-id generation for Spiral/TwoTone/JellyRoll scaffolds.
- Added variant tests validating AroundTheBend wraparound word coordinates and SnakeCharmer overlap/dual-number cell behavior.
- Added variant tests covering Coded mapping/givens, Crosswordle status coloring/word IDs, and DownsOnly clue-clearing + validation behavior.

## 9) Risk controls and rollback
- Status: In progress.
- Kotlin implementation remains untouched and authoritative.
- Python work is additive and isolated under `kotwords_py/`.

## 10) Completion definition
- Status: Not started.
- No completion gates have been satisfied yet.

## 11) Plan review loop (performed and required continuously)
- Status: In progress.
- First pass completed for scope alignment and initial phase kickoff.
