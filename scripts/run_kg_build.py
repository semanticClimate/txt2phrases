#!/usr/bin/env python3
"""Run the KG build logic (same as build_knowledge_graph.ipynb) for testing."""
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MATRIX_CSV = Path(PROJECT_ROOT, "Examples", "otvirare", "india_plant_reports", "keyphrase_matrix.csv")
OUT_DIR = Path(PROJECT_ROOT, "scripts", "kg_output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

INSTITUTION_COLS = ["circot", "cpcri", "ctcri", "iior", "iivr", "iiwbr", "nbpgr", "nrri", "ppvfra", "sbi"]
TOP_N = 100
ALPHA = 0.5
MIN_EDGE_WEIGHT = 1

df = pd.read_csv(MATRIX_CSV)
for c in INSTITUTION_COLS + ["Total", "N_institutions"]:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)

df_sorted = df.sort_values("N_institutions", ascending=False).reset_index(drop=True)
top = df_sorted.head(TOP_N).copy()
keywords = top["keyword"].tolist()

max_total = top["Total"].max()
top["f_total"] = np.log(1 + top["Total"]) / np.log(1 + max_total)
top["f_spread"] = top["N_institutions"] / 10.0
top["node_weight"] = ALPHA * top["f_total"] + (1 - ALPHA) * top["f_spread"]
node_weights = top.set_index("keyword")["node_weight"].to_dict()

def institutions_in_common(row_a, row_b, cols):
    return sum(1 for c in cols if row_a[c] > 0 and row_b[c] > 0)

G = nx.Graph()
for _, r in top.iterrows():
    G.add_node(r["keyword"], weight=node_weights[r["keyword"]])

top_by_kw = top.set_index("keyword")
for i, ka in enumerate(keywords):
    ra = top_by_kw.loc[ka]
    for kb in keywords[i + 1:]:
        rb = top_by_kw.loc[kb]
        w = institutions_in_common(ra, rb, INSTITUTION_COLS)
        if w >= MIN_EDGE_WEIGHT:
            G.add_edge(ka, kb, weight=w)

kg_graphml = Path(OUT_DIR, "keyphrase_kg.graphml")
kg_gexf = Path(OUT_DIR, "keyphrase_kg.gexf")
fig_png = Path(OUT_DIR, "keyphrase_kg.png")

nx.write_graphml(G, kg_graphml)
nx.write_gexf(G, kg_gexf)

fig, ax = plt.subplots(figsize=(14, 14))
pos = nx.spring_layout(G, k=1.5, seed=42, iterations=50)
weights = [G.nodes[n].get("weight", 0.5) for n in G.nodes()]
nx.draw_networkx_nodes(G, pos, node_size=[200 + 400 * w for w in weights], node_color=weights, cmap=plt.cm.viridis, alpha=0.9, ax=ax)
nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)
nx.draw_networkx_labels(G, pos, font_size=6, ax=ax)
ax.set_title("Keyphrase knowledge graph (top 100 by N_institutions)")
ax.axis("off")
plt.tight_layout()
plt.savefig(fig_png, dpi=150, bbox_inches="tight")
plt.close()

print("Nodes:", G.number_of_nodes(), "Edges:", G.number_of_edges())
print("Saved:", kg_graphml, kg_gexf, fig_png)
