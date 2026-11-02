# File formats and manual fallback

Normally never edit these files by hand: use `scripts/tp.py`, which re-reads under a lock and writes atomically (safe with several agents). Read this file only when you cannot run Python, or want to understand a format.

## Location

```
$TINY_PIECES_HOME            default ~/.tiny-pieces  (never inside the project repo)
├── knowledge.md             the dev's profile + prerequisite graph
├── probes.md                optional: the dev's own probes, same format as references/probes.md
└── maps/<slug>.md           one gap map per goal
```

## `knowledge.md`

One row per concept, plus an optional alias list.

```markdown
# Knowledge profile

Status comes from probe results only, never from "yeah I know it".
✅ known · ⚠️ shaky · ❌ gap · ❓ not probed

| Concept | Domain | Status | Needs | Evidence | Verified | Seen in |
|---|---|---|---|---|---|---|
| slope of a line | math | ✅ |  | solved probe in 1 try | 2026-10-29 | micrograd |
| derivative | math | ❌ | slope of a line | couldn't explain d/dx x² at x=3 | 2026-10-29 | micrograd |
| graphs / dfs | cs | ⚠️ | graph | DFS visit order wrong | 2026-10-29 | micrograd |

## Aliases
dérivée = derivative
```

- **Concept:** one canonical name per concept, no `,` or `|`. "Derivative" in micrograd and in a physics course is the same row. Before creating a row, look for the same concept under another wording or language and use `alias` instead.
- **Domain:** one lowercase word (math, python, cs, ml, physics, technique). Used by "what do I know?".
- **Status:** ✅ ⚠️ ❌ ❓.
- **Needs:** direct prerequisites only, comma-separated canonical names. This is the **global prerequisite graph**: written once, reused by every goal. No cycles.
- **Evidence:** what exactly they solved or failed. Mandatory for ✅ ⚠️ ❌. A row with empty Evidence counts as ⚠️ until probed.
- **Verified:** `YYYY-MM-DD` of the last probe. ✅ older than 60 days needs a one-question re-check (`TP_STALE_DAYS` changes the 60).
- **Seen in:** goal slugs, comma-separated.
- **Downgrade rule:** if the dev fails or visibly hesitates on a ✅ at any step, set it to ⚠️ with the new evidence. Upgrade only through a probe or an exit exercise.

## `maps/<slug>.md`

Slug = lowercase-kebab-case of the goal (`micrograd`, `electromagnetism-ch3`).

```markdown
---
goal: micrograd
sentence: A tiny autograd engine that computes gradients of scalar expressions.
project: /home/dev/code/micrograd
created: 2026-10-29
updated: 2026-10-29
---
# Map: micrograd

<!-- tp:begin generated (rebuilt by tp.py, do not edit) -->
## Tree
- micrograd 🎯 root
  - Value class (piece) 🔨 built
    - classes and objects ✅
  - backprop (piece)
    - backpropagation ❌
      - chain rule ❌
        - derivative ❌
          - slope of a line ✅ floor

## Learning order
### 1. Value class
- [x] classes and objects ✅
- [x] BUILD Value class
### 2. backprop
- [x] slope of a line ✅
- [ ] LEARN derivative ❌ - scope: slope + power rule only
- [ ] LEARN chain rule ❌
- [ ] LEARN backpropagation ❌
- [ ] BUILD backprop

## Next
LEARN derivative ❌ - scope: slope + power rule only
<!-- tp:end generated -->

## Pieces
- [x] Value class | needs: classes and objects
- [ ] backprop | needs: backpropagation

## Scopes
- derivative: slope + power rule only; no epsilon-delta

## Later
- Adam optimizer

## Log
- 2026-10-29 built Value class
```

- **The block between the `tp:` markers is generated** from the profile graph plus the Pieces. It is always in sync. Never edit it.
- **Source of truth for a map:** `Pieces` (big pieces in build order, each with the concepts it directly needs), `Scopes` (how deep to go, per concept, for this goal), `Later`, `Log`.
- **Learning order** goes piece by piece: learn a piece's gaps bottom-up, then `BUILD` it, then the next piece. Pieces with no gaps come first (quick win).
- A node shared by two pieces is listed once, under the first piece that needs it.
- Known nodes are floors: the tree does not expand below a ✅. ❓ nodes are probed just in time, and expand once they turn ❌ or ⚠️.

## Manual fallback (no Python)

Do the same by hand, carefully:
1. **Re-read the file right before writing**, then change only the affected row or line. Never rewrite a whole file from memory.
2. Update right after each result, not at the end of the session.
3. For a `knowledge.md` row: set Status, Evidence, Verified (`date +%F`), and add the goal to Seen in. Keep the table aligned to 7 columns.
4. For a map: tick `[x]` on the piece in `Pieces` after it works, add a `Log` line, and rewrite the generated Tree / Learning order / Next by hand (same layout as above).
5. Tell the dev once that the files live in `~/.tiny-pieces/` and any agent can read them.

## No filesystem at all

Keep the profile and the map in the conversation. At the end of each milestone, print both files in code blocks so the dev can save them to `~/.tiny-pieces/`.
