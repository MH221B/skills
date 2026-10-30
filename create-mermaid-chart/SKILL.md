---
name: create-mermaid-chart
description: Create or revise any Mermaid diagram and export a styled SVG with Pele. Use when the user asks for a Mermaid chart, flowchart, sequence diagram, state diagram, architecture diagram, timeline, or an SVG of a Mermaid diagram. Keep the editable .mmd source alongside the SVG; honor requested styling.
---

# Create a Mermaid chart

1. Identify the diagram type from the user's content. Use any Mermaid diagram type that Pele supports; do not default to a state diagram. If an existing `.mmd` is supplied, edit that source rather than recreating it. Ask only when the relationships or output destination cannot be determined.
2. Write readable Mermaid syntax to `<name>.mmd`. Preserve the user's terms and requested content. Put the output beside an existing source or in the user's requested location; otherwise use the working directory. Do not add unrequested nodes or relationships.
3. In a fresh checkout, run `npm ci --prefix <skill-dir> --registry=https://registry.npmjs.org` once. Then run `node <skill-dir>/scripts/render.mjs <name>.mmd [theme.css]`. Pele lives in the skill's ignored `node_modules`; the script writes `<name>.svg` beside the source.
4. If the user requests colors, fonts, light/dark mode, or another visual style, write CSS to `theme.css` beside the diagram and pass it to the script. Consult https://pele.run/theming for supported `--pele-*` variables and `.pele` classes. Scope rules to `.pele`; the script embeds the CSS in the SVG and passes `--pele-font` to Pele when present, so text fits its nodes. Use Mermaid `classDef` or `style` only for requested per-element choices. Without a requested style, omit the CSS file and use Pele's defaults.
5. Check that the SVG exists, starts with `<svg`, and contains the expected labels. Deliver links to both files. Mention any requested styling that cannot be rendered by Pele; keep the Mermaid source usable.

Pele renders Mermaid text into SVG; it does not check the truth of a diagram or model the system. Do not introduce TLA+, TLC, or formal verification unless the user requests them separately.
