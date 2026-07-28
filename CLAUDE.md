# CLAUDE.md — working context for this repo

Guidance for any Claude instance working in `translation-checkup`. Read this before making changes.

## What this project is

Reconciliation of Traveloka POE translation strings across **Android** and **iOS**. Raw POE exports + "cleaned" in-app string lists are pruned, combined, matched across platforms, and each string is classified as **workspace → bucket → key**. Output is `poe.csv`, viewed via `index.html`.

Org context: this is Traveloka (an OTA). Treat all data as internal/confidential. For any BigQuery work, the billing project **must** be `tvlk-shared-bq-dev`.

## Source of truth & artifacts

- **`poe.csv` is the source of truth** — 6 columns: `initial key, initial value, assigned workspace, assigned bucket, assigned key name, is merged`. 16,667 rows.
- `poe.json` and `fuzzy_matches.json` were **intentionally deleted** (redundant with `poe.csv` and the tier files). **Do not recreate them in the repo.** If you need key/value data, read `poe.csv`; if you need the fuzzy pairs, read `fuzzy_matches_tier{A,B,C,D}.json`.
- `source/` holds the raw exports (`androidpoe.json`, `andcleaned.xml`, `iospoe.json`, `ioscleaned.json`).
- Viewer: `index.html` + `make serve` (port 8766). Must be served over `http://`, not `file://`.
- The user previously mirrored this data into a Lark spreadsheet/Base (`https://traveloka.sg.larksuite.com/wiki/Gn9WwPdxwiMZXjk2QOGlDK0igUf`), but has since **moved to the HTML/CSV** — the CSV is authoritative now, don't assume the Lark doc is in sync.

## Data conventions the user established (follow these)

1. **Values** come from the POE `value` field, **never `androidXmlValue`**.
2. **workspace** = product domain, lowercase, from a controlled vocabulary (flight, **hotel**, experience, shuttle, bus, train, rental, cruise, payment, paylater, refund, ptp, trip, credit, pricealert, kyc, user, postbooking, common, package). Blank if not confident. (The accommodation domain is canonicalized to workspace `hotel` — variants `accommodation`/`accomm`/`accom`/`hotel` all map to `hotel`.)
3. **bucket** = feature-level grouping only, prefixed by the string's **domain** (usually = the workspace). A bucket name must never be shared across workspaces. **Special cases** (workspace ≠ bucket prefix): the `hotel` workspace keeps bucket prefix `accom` (`accom_tnc`, not `hotel_tnc`); `pricealert` strings live in the `flight` workspace but keep bucket prefix `pricealert` (`pricealert_revamp`). Modeled in the parser as a DOMAIN→bucket-prefix map plus a WS_OF domain→workspace override. Some domains are spelled differently per platform — e.g. iOS `pricealert` vs Android's two-token `price_alert`; a MULTI map folds such multi-token leading forms into one domain (both → `pricealert`). The iOS `travelokapay` namespace maps to the `paylater` domain/workspace. The `postbooking` workspace collects three leading prefixes: `postbooking`, `itinerary`, and the multi-token `booking_trip_based_my_booking` (the last takes precedence over the `trip` token inside it). `tpay` also maps to `paylater` (it's short for travelokapay). Two new workspaces: `common` (leading `common` prefix, e.g. `text_common_*`; single bucket `common`, detail in key) and `package` (leading `package` prefix). Two feature overrides (match the token anywhere in the key): `columbus` → workspace `experience`, single bucket `experience_columbus`; `my_cards`/`my-cards` → workspace `payment`, single bucket `payment_my_cards`.

**Value-matched pairs & merging:** when an Android key and an iOS key share the same (normalized) value, derive workspace/bucket/key from the iOS key's dot-structure — workspace = iOS domain, bucket = workspace-prefixed segment after the domain (e.g. `payment_refund_balance`), key = everything after that segment with element markers kept (`label_about`) — and apply the SAME assignment to both keys with `is merged = TRUE`.

**price-alert consolidation:** all price-alert strings (any key containing `pricealert` / `price_alert`, incl. `text_banner_price_alert_*` and `navigation_menu_price_alert`) live in workspace `flight` under a single bucket **`price_alert`** — no feature sub-buckets. Everything else moves into the key: the iOS `revamp` token is dropped; Android feature words (`detail`/`form`/`homepage`/`enable`/`remove`/…) become the key prefix; `text_banner_price_alert_*` keeps a `banner_` key prefix; `navigation_menu_price_alert` → key `navigation_menu_price`.
4. **bucket is feature-only; all extra detail goes into the key.** Default rule: feature = the first token after the workspace prefix; everything after moves into the key. (Accommodation has a hand-refined feature map with a few 2-token features and semantic merges, e.g. `pay_at_hotel`→`pah`, `check_out`→`check_in`, all `no_*`→`no_inventory_handling`.)
5. **key** = the content leaf, snake_case, with **template symbols stripped** (`%@`, `%ld`, `%d`, `{0}`, `(%@)`).
6. **Fill only when confident; leave blank otherwise.** Wrong values are worse than blanks.
7. **`is merged`**: `TRUE` for merged tier-A pairs, `FALSE` for unique keys (no cross-platform match), blank for keys that have a match but aren't merged yet.
8. **Merged pairs must be identical**: for every tier-A pair, the Android and iOS rows share one identity (derived from the Android key) → same bucket + key. Where a key fuzzy-matched multiple partners, keep the most-specific pair merged and **unmerge the extras** (they keep their own distinct identity, `is merged = FALSE`). Don't force distinct interfaces to collide.
9. **Uniqueness**: distinct interfaces should not collapse to the same `bucket`+`key`. Collapsing buckets is fine because the detail moved into the key keeps rows distinct.

## Classification pipeline

The parser lives in scratchpad as `poeparse.py` (regenerable — see below), not committed. Its logic:
- Strip `andpoe.`/`iospoe.` prefix and a leading `text_` (Android).
- workspace = first token mapped via the vocabulary above (Android and iOS variants: `accommodation`/`accomm`/`accom`/`hotel`→`hotel` (bucket prefix stays `accom`), `car`/`vehicle`→rental, `pay`→payment, `point`→ptp, etc.).
- Android: split bucket at the last page/container marker (`result`, `detail`, `page`, `popup`, `tray`, `list`, `tab`, `section`, `dialog`, …); iOS: split at the element marker (`label`, `button`, `title`, `text`, …). Then collapse bucket to the first-token feature and push the rest into the key.
- Cross-platform matching: 1,400 exact + 2,674 fuzzy (tiers A–D by byte-exact value equality). Merged set = tier A.

## Keeping this file current (standing agreement)

**Auto-on-new-rule:** whenever the user establishes a durable convention or preference, update this CLAUDE.md in the same turn and briefly note that you did (the change shows up in the diff/commit). Capture genuine rules/preferences only — not one-off actions or transient state. When in doubt whether something is durable, add it; the user can prune.

## Workflow preferences

- The user works **iteratively**: apply a change, they review the data directly, then give corrections. Expect follow-up refinements.
- **Don't commit/push unless asked.** When pushing: repo is `ivandwijaya/translation-checkup` (private), commit to `main`, end commit messages with the `Co-Authored-By: Claude ...` trailer.

## Practical gotchas

- The **scratchpad is cleared between sessions.** `poeparse.py` and intermediate files won't persist. Regenerate the parser from `poe.csv` + the tier files; it's deterministic, so re-running reproduces the committed data.
- **Bash `cd` in a compound command can silently fail** in this environment — use absolute paths.
- **The in-app browser blocks `localhost`**, so you can't screenshot the local viewer; verify by serving + `curl` instead.
- Lark: use `--as user`. To add records use `base +record-batch-create` (≤200/batch); for distinct per-row updates use `base +record-upsert` per record (`+record-batch-update` only applies one shared patch). Pass large JSON via a direct arg through Python `subprocess`, not shell (avoids quoting issues); `--json -` stdin and `@file` with absolute paths don't work.
- The viewer is published via GitHub Pages at https://ivandwijaya.github.io/translation-checkup/ (also runs locally via `make serve`). A Pages site is publicly reachable, so the dataset — including internal key names/codenames — is exposed on the public internet.

## Current status

All 17 workspaces have been collapsed to feature-level buckets (~5,800 raw buckets → ~1,000 features). Accommodation uses the user's refined map; the rest use the first-token default. Merged tier-A pairs are verified identical across platforms (0 mismatches); cross-workspace bucket conflicts: 0. `STATS.md` predates the bucket work and may be stale.
