# translation-checkup

Reconciliation of Traveloka POE translation strings across **Android** and **iOS**.

Takes the raw POE exports and the "cleaned" in-app string lists for each platform, prunes each POE export down to the strings actually shipped, combines them into a single key→value dataset, detects strings duplicated across platforms, and assigns each string a **workspace → bucket → key** classification derived from its key name.

## Preview locally

`poe.csv` is the dataset (16,667 rows). `index.html` is a searchable, paginated viewer for it. It must be served over `http://` — opening the file directly (`file://`) won't work, because the browser blocks the CSV `fetch()`.

```bash
make serve
# then open http://localhost:8766/
```

(`make serve PORT=9000` to change the port. Equivalent to `python3 -m http.server 8766`.)

Viewer features:
- Search across key, value, bucket, and key name
- **Filter by assigned workspace**
- Filter by merged status (TRUE / FALSE / blank)
- **Sort any column alphabetically** (click the header; click again to reverse)
- Adjustable page size

> The viewer is fully client-side; nothing is uploaded. (GitHub Pages isn't used — Pages needs a public repo or a paid plan for private repos.)

For a quick look without a server, open `poe.csv` in Excel, Numbers, or VS Code.

## Data columns (`poe.csv`)

| Column | Meaning |
|--------|---------|
| `initial key` | Original POE bucket name (`andpoe.*` / `iospoe.*`). |
| `initial value` | The POE `value` (English string). |
| `assigned workspace` | Product domain inferred from the key (e.g. `flight`, `accommodation`, `payment`). Blank if uncertain. |
| `assigned bucket` | Feature-level grouping, workspace-prefixed (e.g. `flight_reschedule`). Blank if uncertain. |
| `assigned key name` | The content leaf (detail beyond the feature), template symbols stripped. |
| `is merged` | `TRUE` if this Android/iOS pair was merged (tier-A), `FALSE` if unique, blank if a match exists but isn't merged yet. |

## Files

| File | Description |
|------|-------------|
| `poe.csv` | The dataset — 6 columns above, 16,667 rows. Source of truth. |
| `index.html` | Local web viewer for `poe.csv`. |
| `Makefile` | `make serve` launcher. |
| `STATS.md` | Reconciliation statistics and rules. |
| `ios_missing_keys.json` | 109 keys in `ioscleaned.json` with no source in `iospoe.json`. |
| `fuzzy_matches_tierA.json` | Identical value (byte-exact) + strong key similarity — 811 pairs (the merged set). |
| `fuzzy_matches_tierB.json` | Identical value (byte-exact) + moderate key similarity — 1,438 pairs. |
| `fuzzy_matches_tierC.json` | Different value + strong key similarity — 120 pairs. |
| `fuzzy_matches_tierD.json` | Different value + weaker key similarity — 305 pairs. |
| `source/androidpoe.json` | Raw Android POE export (23,242 buckets). |
| `source/andcleaned.xml` | Cleaned Android strings (8,930 `<string>` entries). |
| `source/iospoe.json` | Raw iOS POE export (23,346 buckets). |
| `source/ioscleaned.json` | Cleaned iOS strings (7,846 keys). |

## How it was built

**Reconciliation**
- **Keys** = original bucket `name` (`andpoe.*` / `iospoe.*`); **values** = the POE `value` field.
- **Android** cleaned name = bucket name lowercased, non-alphanumeric runs → `_`, with the stringList key appended (`_text`).
- **iOS** cleaned key = bucket name + `.` + stringList key (`.text`), `iospoe.` prefix kept.
- Only buckets whose cleaned key appears in the corresponding cleaned file are kept, then combined into `poe.csv`.

**Cross-platform matching**
- 1,400 exact (normalized) key matches + 2,674 fuzzy matches (key-name context + value similarity), tiered by byte-exact value equality (tiers A–D).
- **Merged** = tier-A pairs, sharing one Android-derived identity. Where one key fuzzy-matched several partners, only the most-specific pair is merged; the extras stay distinct and `is merged = FALSE`. Every merged pair has identical bucket + key on both platforms.

**workspace → bucket → key classification**
- Parsed from each key name: `workspace` from a controlled domain vocabulary; `bucket` = workspace-prefixed feature; `key` = the remaining detail. Filled only when confident, blank otherwise.
- **Bucket granularity** is collapsed to feature level (the first token after the workspace, plus manual refinements for accommodation), with the removed detail pushed into the key. Buckets are workspace-prefixed, so no bucket name is shared across workspaces.

See `STATS.md` for the full numbers.
