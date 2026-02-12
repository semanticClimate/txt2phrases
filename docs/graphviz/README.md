# Graphviz diagrams

Diagrams for txt2phrases structure and data flow. See **summary.md** for a short description of what each diagram shows.

| File | Description |
|------|--------------|
| **static.dot** | Static view: package modules and their dependencies (internal and external). |
| **flow.dot** | Data flow: pipelines from inputs (PDF, HTML, TXT) to outputs (CSV, merged, classification). |

## Rendering

From this directory (or project root):

```bash
# SVG (good for docs and browsers)
dot -Tsvg -o static.svg static.dot
dot -Tsvg -o flow.svg flow.dot

# PNG
dot -Tpng -o static.png static.dot
dot -Tpng -o flow.png flow.dot
```

Requires [Graphviz](https://graphviz.org/) (`brew install graphviz` on macOS).
