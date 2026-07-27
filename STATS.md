# Translation Checkup — Statistics

Cross-platform (Android / iOS) POE string reconciliation.

## Source files (`source/`)

| File | Entries |
|------|--------:|
| `androidpoe.json` (buckets) | 23,242 |
| `andcleaned.xml` (`<string name>`) | 8,930 |
| `iospoe.json` (buckets) | 23,346 |
| `ioscleaned.json` (`content` keys) | 7,846 |

- Every bucket in both POE files has exactly **1** `stringList` member.
- All iOS buckets use stringList key `"text"`.

## Cleaning / pruning rules

- **Android:** cleaned XML name = JSON `name` lowercased, non-alphanumeric runs → `_`, with the stringList key appended (`_text`). e.g. `andpoe.about_withdrawal_process` → `andpoe_about_withdrawal_process_text`.
- **iOS:** cleaned key = JSON `name` + `.` + stringList key (`.text`); `iospoe.` prefix retained. e.g. `iospoe.payment.partner.installment.title`.
- Values use the `value` field (not `androidXmlValue`).

## Intersection: cleaned vs POE source

| Platform | Cleaned keys | Matched in POE | Missing from POE |
|----------|-------------:|---------------:|-----------------:|
| Android | 8,930 | 8,930 (100%) | 0 |
| iOS | 7,846 | 7,737 | **109** |

- Android intersects perfectly.
- iOS has **109 keys present in `ioscleaned.json` but absent from `iospoe.json`** (different format — no `iospoe.` prefix / `.text` suffix). Listed in `ios_missing_keys.json`. Cross-check vs androidpoe found **0** name matches and only 58 value matches (24 unique, 34 ambiguous) — not reliably sourceable from Android.

## Combined output → `poe.json`

| Source | Entries |
|--------|--------:|
| Android | 8,930 |
| iOS | 7,737 |
| Key overlap | 0 |
| **Total** | **16,667** |

Keys = original bucket `name` (`andpoe.*` / `iospoe.*`); values = `value` field.

## Cross-platform key duplication (Android ↔ iOS)

Matching by normalized key name (prefix stripped) plus value similarity, since keys are entered manually by engineers.

| Match type | Count |
|-----------|------:|
| Exact (identical normalized key) | 1,400 |
| Fuzzy (non-exact key + value) | 2,674 |
| **Total shared keys** | **4,074** |

≈ 46% of Android and ≈ 53% of iOS cleaned keys have a cross-platform counterpart.

### Fuzzy match tiers (`fuzzy_matches_tier*.json`)

Value equality is **byte-exact and case-sensitive**. Any difference — including case-only — is treated as a different value and separated into tiers C/D.

| Tier | Criteria | Count |
|------|----------|------:|
| A | **Identical value** (byte-exact) + strong key sim (≥0.6) | 811 |
| B | **Identical value** (byte-exact) + moderate key sim (0.4–0.6) | 1,438 |
| C | **Different value** + strong key sim (≥0.6) | 120 |
| D | **Different value** + weaker key sim (<0.6) | 305 |
| | **Total** | **2,674** |

- Identical-value pairs (A+B): **2,249**
- Different-value pairs (C+D): **425** — of the 120 tier-C pairs, 35 differ only by capitalization (cross-platform inconsistencies worth reviewing).

Each tier file carries a `value_identical` boolean per pair. Full pairs with scores and both values: `fuzzy_matches.json` (and per-tier splits).

## Value overlap (informational)

- Distinct value strings shared by both platforms: **3,679**
- Android: 8,930 entries → 6,595 distinct values
- iOS: 7,737 entries → 5,486 distinct values
