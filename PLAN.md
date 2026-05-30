# PLAN: Full Kotlin-to-Python Conversion for kotwords

## 1) Objective
Convert the entire `kotwords` codebase from Kotlin Multiplatform to Python while preserving behavior, format compatibility, test coverage expectations, and release capabilities (library + CLI + web tooling equivalent).

## 2) Scope and parity targets
- **In scope**
  - Core puzzle/domain models (`model/*`)
  - All format readers/writers in `formats/*` (including JSON/XML/ZIP/AcrossLite/JPZ/IPUZ/PDF and site-specific adapters)
  - CLI behavior now in `nativeMain/cli/Main.kt`
  - Web-tooling behavior currently in `jsMain/web/*` + `jsMain/resources/*`
  - Test corpus and behavior parity with current `commonTest`, `jvmTest`, `jsTest`, `nativeTest`
- **Out of scope (unless explicitly approved)**
  - Feature additions beyond parity
  - Format semantic changes that break existing users

## 3) Baseline inventory (must be frozen before migration)
1. Record all public API entry points and signatures from:
   - `com.jeffpdavidson.kotwords.model.*`
   - `com.jeffpdavidson.kotwords.formats.Puzzleable` and conversion methods
2. Record all supported formats from CLI `Format` enum and extension mappings.
3. Freeze test resources under `src/commonTest/resources/**` as canonical fixtures.
4. Produce a feature matrix from tests (format x behavior x edge cases).
5. Capture current CI behavior and artifact outputs (library, CLI binaries, web dist).

### 3.1) Generated/static asset migration requirements
- Preserve behavior of generated or large static sources, especially:
  - `formats/unidecode/*` transliteration tables
  - `formats/pdf/BuiltInFontMetrics.kt` equivalent metrics data
  - web HTML/resources and icons in `src/jsMain/resources/*`
- Decide and document whether these are:
  - copied as static Python data files, or
  - regenerated from source scripts with reproducible build steps
- Add checksum-based tests to detect accidental drift in migrated generated assets.

## 4) Target Python architecture
- Package layout:
  - `kotwords_py/model/`
  - `kotwords_py/formats/`
  - `kotwords_py/formats/json/`
  - `kotwords_py/formats/pdf/`
  - `kotwords_py/web/`
  - `kotwords_py/cli/`
  - `tests/fixtures/` (mirrored from existing resources)
- Core implementation rules:
  - `dataclasses` + `Enum` for domain models
  - explicit immutability policy where Kotlin data classes imply value semantics
  - consistent byte/str boundaries for binary formats
  - deterministic serialization where output snapshots are compared
- Compatibility layer:
  - keep a thin Kotlin-to-Python mapping document for each class/function migrated

## 5) Dependency mapping plan
Map each Kotlin dependency to a Python equivalent before coding:
- `kotlinx.serialization` / json models -> `pydantic` or `dataclasses` + `orjson/json`
- XML parsing abstractions (`Xml expect/actual`) -> `lxml` (preferred) or `xml.etree` + selector helper
- ZIP operations (`Zip expect/actual`) -> `zipfile`
- CP1252/URL/entity logic (`Encodings`) -> Python codecs + `urllib.parse` + `html.unescape`
- coroutines/mutex usage -> `asyncio` + `asyncio.Lock` only where needed
- PDF generation stack -> a single chosen Python PDF engine (must support font metrics + embedded TTF)

## 6) Migration order (phased, risk-first)
### Phase A: Foundation and shared types
1. Implement Python `Puzzle`, `Crossword`, and all variety model types.
2. Port utility behavior (`Strings`, shared constants, validation semantics).
3. Build shared exceptions (`InvalidFormatException`, invalid ZIP/format equivalents).
4. Add contract tests for model invariants (grid rectangularity, clue/word integrity, solution presence).

### Phase B: Platform abstraction equivalents
1. Implement Python replacements for `Encodings`, `Xml`, and `Zip` with cross-platform consistency.
2. Add edge-case tests for:
   - CP1252 encode/decode unsupported chars
   - HTML entity decoding parity
   - URL decoding behavior
   - ZIP first-entry semantics and invalid ZIP errors

### Phase C: Core format engines
Port in this order (lowest to highest coupling):
1. `AcrossLite`, `Ipuz`, `Jpz`, `Xd`, `Pzzl`, `Rgz`
2. Site/source adapters (`Guardian`, `NYT`, `PuzzleMe`, `WSJ`, `Uclick*`, etc.)
3. Composite/delegating puzzleable flows

For each format:
- add fixture-based parse tests
- add write/read roundtrip tests
- add differential tests against Kotlin outputs (golden snapshots)

### Phase D: PDF pipeline
1. Port PDF document primitives and font abstractions (`PdfDocument`, fonts, TTF parsing hooks).
2. Port rendering logic (`Pdf.asPdf`, grid drawing).
3. Validate output using structural PDF checks + visual regression sampling.
4. Validate font fallback and embedded-font parity.

### Phase E: CLI and web parity
1. Rebuild CLI command surface (`convert`, `dump-entries`) with identical flags/semantics.
2. Rebuild web generation flow currently driven by JS forms/resources.
3. Preserve input/output conventions (stdin/stdout, file extension inference, defaults).
4. Add end-to-end CLI tests over fixture corpus.

### Phase F: Packaging and release
1. Publish Python package (wheel + sdist) with semantic versioning policy.
2. Replace Gradle CI with Python CI matrix (Linux/macOS/Windows).
3. Produce release artifacts replacing existing CLI binaries strategy.
4. Update docs (`README`, API docs, usage examples).

### Phase G: Cutover and deprecation
1. Run a release-candidate period where Kotlin and Python implementations both ship.
2. Mark Kotlin implementation as deprecated only after parity gates stay green across at least one full release cycle.
3. Publish migration notes for downstream users (API changes, behavior differences if any, rollout timeline).
4. Remove Kotlin implementation only after explicit sign-off.

## 7) Testing and verification strategy
- **Differential parity harness (required):**
  - run Kotlin implementation and Python implementation over same fixtures
  - compare normalized puzzle objects and output bytes where deterministic
- **Test layers:**
  - unit tests: model, encoding, parser units
  - fixture tests: all existing resources
  - roundtrip tests: format write->read->equivalence
  - end-to-end tests: CLI commands and web flow
- **Acceptance threshold:**
  - no regressions on supported fixtures unless explicitly documented
  - identical or intentionally normalized output for critical formats (PUZ/JPZ/IPUZ/PDF metadata expectations)
  - no unplanned performance regressions for large puzzles (parse, convert, PDF generation)

### 7.1) Traceability requirements
- Every Kotlin source file must map to one of:
  1. Python implementation file
  2. Explicitly retired feature decision
  3. Replaced external dependency with parity proof
- Maintain a migration matrix (`kotlin file -> python file/tests`) and require it to be complete before cutover.

## 8) Edge cases that must be explicitly covered
- HTML clues vs plain text clues and sanitizer behavior
- unsupported feature flags (`hasUnsupportedFeatures`, diagramless handling)
- clue list merging semantics and non-standard directions
- border-aware numbering and word-boundary logic
- void/blocked/circled/shaded/image cells
- multiple answers / hints / top-right numbering
- date/author/copyright defaulting behavior used by CLI adapters
- compressed and malformed input files (bad ZIP/XML/JSON/binary)
- Unicode normalization and CP1252 fallback substitution
- deterministic ordering of clues/words and stable serialization
- cached parsing behavior (equivalent semantics to `Puzzleable.asPuzzle()` memoization)
- malformed/partial online-source payloads from site-specific adapters
- PDF layout edge cases: long clues, font fallback, non-Latin glyph handling, image cells

## 9) Risk controls and rollback
- Keep Kotlin as reference implementation until parity gate is passed.
- Migrate feature-by-feature behind explicit completion checkpoints.
- Do not remove Kotlin source until:
  - parity checklist is green
  - CI is green on all supported OSes
  - release dry run succeeds

## 10) Completion definition
Migration is complete only when all are true:
1. Every supported format in current CLI enum is implemented in Python.
2. Fixture-based tests and differential parity checks pass.
3. CLI parity tests pass for documented commands and flags.
4. Web workflow parity is demonstrated for all puzzle generation forms.
5. Python package + release pipeline are operational and documented.
6. Traceability matrix is complete with no unmapped Kotlin files.
7. Generated/static asset parity checks are green.

## 11) Plan review loop (performed and required continuously)
Use this loop at each milestone and before declaring readiness:
1. **Coverage pass:** confirm each Kotlin package/file has a mapped Python destination.
2. **Behavior pass:** confirm each current test has Python equivalent coverage.
3. **Edge-case pass:** confirm section 8 is represented in tests.
4. **Interface pass:** confirm API/CLI/web contracts stay backward compatible.
5. **Release pass:** confirm packaging/CI/docs are updated for migrated scope.

If any pass fails, update the plan/tasks and re-run the full loop before proceeding.
