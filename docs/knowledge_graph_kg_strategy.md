# Knowledge graph (KG) from keyphrase_matrix.csv – strategy proposal

**Date:** 2026-02-16 (system date)  
**Conventions:** amilib style guide (`../amilib/docs/style_guide_compliance.md`); absolute imports; `Path()` with multiple args; no `sys.path`; system date where relevant.

**Status:** Proposal only. Not implemented. For inspection.

---

## 1. Input

- **Source:** `Examples/otvirare/india_plant_reports/keyphrase_matrix.csv`
- **Rows:** Keyphrases (one per row) → **nodes** of the KG.
- **Columns:**  
  - **Institution columns (10):** `circot`, `cpcri`, `ctcri`, `iior`, `iivr`, `iiwbr`, `nbpgr`, `nrri`, `ppvfra`, `sbi`.  
  - **Derived:** `Total` (sum of cell values), `N_institutions` (number of non-blank institution cells, 0–10).
- **Cell values:** Count (integer) or blank (treated as 0).

---

## 2. Node weight

**Goal:** A single weight per node (keyphrase) that reflects both **how much** it appears (total count) and **how widely** it appears (spread across institutions), without letting large totals dominate.

**Components:**

- **Total occurrences:** `Total` column = sum of counts across the 10 institution columns. Range in current data is roughly 1–857 (and could grow).
- **Spread:** `N_institutions` = number of non-zero institution columns (0–10). Already in the CSV.

**Proposed function (normalised, 0–1 scale):**

- **Total component:** Use a damped scale so large values do not swamp. For example:
  - `f_total = log(1 + Total) / log(1 + max_Total)` over all nodes, or
  - `f_total = sqrt(Total) / sqrt(max_Total)`, or
  - Min–max normalisation of `log(1 + Total)` across nodes.
  So `f_total` is in [0, 1] (or close), with diminishing returns for very large totals.

- **Spread component:** `f_spread = N_institutions / 10` (already 0–1).

- **Combined weight:**  
  `node_weight = α * f_total + (1 − α) * f_spread`  
  with `α` in [0, 1] (e.g. 0.5 for equal mix). Alternatively:
  - `node_weight = f_total * (0.5 + 0.5 * f_spread)` so that spread modulates total.
  - Or geometric mean: `node_weight = sqrt(f_total * f_spread)`.

**Recommendation:** Start with **α = 0.5** and **f_total = log(1 + Total) / log(1 + max_Total)** so that (1) weights are in a bounded range and (2) high-total keyphrases don’t overwhelm; tune α after inspecting the distribution.

---

## 3. Edges

**Goal:** Connect keyphrases that co-occur in the same institutions (shared “footprint”).

**Proposed definition:**

- **Edge weight:** For two nodes (keyphrases) A and B, count how many **institution columns** have a non-zero value for **both** A and B. That count is in **0–10** (number of institutions in common).
- **When to create an edge:** Only if “institutions in common” ≥ 1 (or a higher threshold, e.g. 2, to reduce noise).
- **Undirected:** Edge (A, B) is the same as (B, A); one undirected edge per pair with weight = number of institutions in common.

**Refinements (optional, not implemented):**

- **Jaccard-style:** weight = |institutions in common| / |institutions in union| (0–1).
- **Weighted overlap:** sum over shared institutions of something like `min(count_A, count_B)` or a product term, then normalise; emphasises not only “both present” but “both with high count”.
- **Threshold:** Only draw edges with weight ≥ 2 (or 3) to keep the graph readable.

**Recommendation:** Implement the simple “count of institutions in common” first; optionally add a minimum threshold (e.g. ≥ 2) and/or cap the number of edges per node (e.g. top-k by weight).

---

## 4. Prototype scope (when implemented)

To keep the first version tractable and interpretable:

1. **Node set:**  
   - Order rows by **N_institutions** (number of non-zero institution columns), descending.  
   - Take the **top 100** keyphrases as nodes.  
   Rationale: keyphrases that appear in many institutions are good candidates for a cross-institution KG; 100 nodes is enough to see structure without clutter.

2. **Edge set:**  
   - Among these 100 nodes, compute pairwise “institutions in common” (0–10).  
   - Create an edge only if that count ≥ 1 (or a chosen threshold).  
   - Edge weight = that count (or a normalised variant as above).

3. **Node weight:**  
   - For these 100 nodes only, compute the proposed node weight (e.g. α * f_total + (1−α) * f_spread) using the full matrix’s `Total` and `N_institutions` (or recompute from the 10 columns).

No other columns or external data are required for this prototype.

---

## 5. Output (proposed, not format-prescribing)

- **Nodes:** List or table: `keyword`, `node_weight`, and optionally `Total`, `N_institutions`, `f_total`, `f_spread` for inspection.
- **Edges:** List or table: `keyword_A`, `keyword_B`, `edge_weight` (and optionally normalised weight).
- **Serialisation:** Format TBD (e.g. CSV for nodes and edges, or a graph format such as GraphML/JSON for use in a visualiser or library). No implementation in this document.

---

## 6. Refinements and alternatives (for later)

- **Node set:** Instead of top 100 by N_institutions, use top 100 by the **node_weight** defined above; or a mix (e.g. require N_institutions ≥ 2 then sort by node_weight).
- **Edge threshold:** Require at least 2 (or 3) institutions in common to reduce very weak links.
- **Direction:** Keep edges undirected; if needed later, direction could encode something else (e.g. “A appears in a superset of B’s institutions”).
- **Largest component:** After building the graph, optionally restrict to the largest connected component for visualisation.
- **Performance:** For 100 nodes, pairwise overlap is 4,950 pairs; for full 1,664 rows it would be ~1.4M pairs—so prototype with 100 nodes is sensible; scaling would need filtering or sampling.

---

## 7. Summary

| Aspect        | Proposal |
|---------------|----------|
| **Nodes**     | Keyphrases (row titles); prototype: top 100 by N_institutions. |
| **Node weight** | Mixture of normalised total (e.g. log-scaled) and spread (N_institutions/10); α=0.5; formula to avoid large totals swamping. |
| **Edges**     | Undirected; weight = number of institution columns where both keyphrases have non-zero count (0–10); optional minimum threshold. |
| **Prototype** | 100 nodes, edges among them only; no implementation in this document. |

This strategy is ready for inspection and tuning (e.g. α, f_total, edge threshold, node ordering) before any implementation.

---

## 8. Implementation: build and display (post-implementation)

The KG is built by the notebook `scripts/build_knowledge_graph.ipynb` (and test-run by `scripts/run_kg_build.py`). Outputs are written to `scripts/kg_output/`:

- `keyphrase_kg.graphml` – GraphML (networkx, Gephi, etc.)
- `keyphrase_kg.gexf` – GEXF (Gephi)
- `keyphrase_kg.png` – matplotlib figure

### Commands to build and display the KG

**Build (run notebook or script):**

```bash
# From repo root: run notebook interactively
jupyter notebook scripts/build_knowledge_graph.ipynb

# Or execute notebook (if kernel is available)
jupyter nbconvert --to notebook --execute scripts/build_knowledge_graph.ipynb

# Or run the Python runner (no Jupyter)
python scripts/run_kg_build.py
```

**Display the KG:**

```bash
# Open the saved PNG
open scripts/kg_output/keyphrase_kg.png

# Or on Linux
xdg-open scripts/kg_output/keyphrase_kg.png
```

**Load and display in Python (e.g. in a REPL or notebook):**

```python
import networkx as nx
from pathlib import Path

G = nx.read_graphml(Path("scripts/kg_output/keyphrase_kg.graphml"))
# Optional: draw with matplotlib
import matplotlib.pyplot as plt
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, font_size=6)
plt.show()
```

**Open in Gephi (or other graph tools):** Open `scripts/kg_output/keyphrase_kg.gexf` or `keyphrase_kg.graphml` in Gephi for layout and filtering.
