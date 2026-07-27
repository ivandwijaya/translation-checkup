# translation-checkup

Reconciliation of Traveloka POE translation strings across **Android** and **iOS**.

Takes the raw POE exports and the "cleaned" in-app string lists for each platform, prunes each POE export down to the strings actually shipped, combines them into a single key→value map, and detects strings duplicated across platforms.

## Preview the CSV locally

`poe.csv` is large (16,667 rows). `index.html` is a searchable, paginated viewer for it. It must be served over `http://` — opening the file directly (`file://`) won't work, because the browser blocks the CSV `fetch()`.

```bash
python3 -m http.server 8765
# then open http://localhost:8765/ in your browser
```

Features: search by key and/or value, filter by platform (Android / iOS), adjustable page size.

> **Note:** This viewer was originally intended for GitHub Pages, but Pages requires a public repo or a paid plan for private repos — so it runs locally instead. Everything is client-side; nothing is uploaded.

For a quick look without a server, open `poe.csv` in Excel, Numbers, or VS Code.

## Files

| File | Description |
|------|-------------|
| `poe.json` | Combined Android + iOS key→value map (16,667 entries). |
| `poe.csv` | Same data as CSV (`key,value`), 16,667 rows. |
| `index.html` | Local web viewer for `poe.csv`. |
| `STATS.md` | Full reconciliation statistics and rules. |
| `ios_missing_keys.json` | 109 keys in `ioscleaned.json` with no source in `iospoe.json`. |
| `fuzzy_matches.json` | All cross-platform fuzzy key matches (Android ↔ iOS) with scores. |
| `fuzzy_matches_tierA.json` | Identical value (byte-exact) + strong key similarity — 811 pairs. |
| `fuzzy_matches_tierB.json` | Identical value (byte-exact) + moderate key similarity — 1,438 pairs. |
| `fuzzy_matches_tierC.json` | Different value + strong key similarity — 120 pairs. |
| `fuzzy_matches_tierD.json` | Different value + weaker key similarity — 305 pairs. |
| `source/androidpoe.json` | Raw Android POE export (23,242 buckets). |
| `source/andcleaned.xml` | Cleaned Android strings (8,930 `<string>` entries). |
| `source/iospoe.json` | Raw iOS POE export (23,346 buckets). |
| `source/ioscleaned.json` | Cleaned iOS strings (7,846 keys). |

## How it was built

- **Keys** = original bucket `name` (`andpoe.*` / `iospoe.*`). **Values** = the POE `value` field.
- **Android** cleaned name = bucket name lowercased, non-alphanumeric runs → `_`, with the stringList key appended (`_text`).
- **iOS** cleaned key = bucket name + `.` + stringList key (`.text`), `iospoe.` prefix kept.
- `poe.json` keeps only buckets whose cleaned key appears in the corresponding cleaned file.
- **Cross-platform duplicates**: 1,400 exact (normalized) key matches + 2,674 fuzzy matches (key-name context + value similarity), tiered by byte-exact value equality.

See `STATS.md` for the full numbers.
