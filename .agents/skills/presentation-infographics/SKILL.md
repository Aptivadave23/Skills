---
name: presentation-infographics
description: Create presentation-ready raster infographics in a polished card-based style. Use whenever the user asks for an infographic, especially for a note, proposal, or technical document; defer to an explicitly requested visual direction.
---

# Presentation Infographics

Create a standalone raster infographic that makes the user's main relationship, decision, or sequence easy to scan. Use the built-in image-generation tool. Do not substitute a Markdown diagram, Mermaid chart, or thin flowchart unless the user asks for one.

## Style

- Use a warm off-white or very light neutral background; dark ink-blue text; restrained blue, green, violet, and orange accents.
- Prefer a clear title, three to five rounded cards or panels, large numbered steps or zones, actual logos for named products/services, subtle directional connectors, and one concise takeaway bar when it adds value.
- Keep labels large and sparse. Favor short phrases over explanatory paragraphs; never rely on tiny text.
- Give each card enough whitespace. Use color to group concepts, not as decoration.
- For document- or project-bound infographics, default to a horizontal 16:9-style canvas unless the target document or user specifies another aspect ratio. Chat-only work may use the orientation that best serves the request.
- Make the composition presentation-ready: clean, flat, readable, and unwatermarked. Avoid photo-realism, stock-photo scenes, dense tables, 3-D decoration, gradients that reduce contrast, and a generic corporate slide aesthetic.

## Workflow

1. Use the target document section when one exists; otherwise use the user's request and relevant chat context. Identify its single visual argument and reuse the supplied terminology for labels.
2. Inspect two or three nearby infographics only when the project already has them. Match the local document's typography, palette, and level of detail; otherwise use this skill's default visual language.
3. Identify every product or service that will be named in a panel. Before generation, look for its real logo locally, then in the product's official brand assets. Supply each acquired logo as a reference/input to the image-generation work; do not expect a text-only prompt to reproduce a logo accurately. A generic icon is not an acceptable substitute for a named product/service with an available logo. If no usable official asset can be obtained, say so before completing rather than silently substituting an icon.
4. Build a concise `infographic-diagram` generation brief: title, one-sentence purpose, ordered cards/zones, exact short labels, the required logo for each named product/service, connectors, palette, and one takeaway if useful. Do not invent or approximate logos.
5. Generate the raster infographic with the image-generation tool, then inspect it at full size before completing. For document-bound work, verify the canvas is horizontal and approximately 16:9 unless another ratio was requested. Also verify that text is correct and readable; each named product/service has its actual undistorted logo rather than a generic icon; card outlines, headings, icons/logos, and body text align to a consistent grid; padding and card gaps are visually even; connectors land cleanly; and nothing is clipped, crowded, stretched, or overlapping. Make targeted revisions until every check passes.
6. For a document or project, save the approved image beside it in the local `images/` convention using a descriptive kebab-case filename, and add or update the Markdown embed with useful alt text when asked. For chat-only work, render the approved image inline and report its saved path; do not create or alter a document.

For detailed cues and local EEH exemplars, read [references/established-style.md](references/established-style.md).

## Boundaries

- Preserve an existing image unless the user explicitly asks to replace it; create a versioned sibling instead.
- If the user gives a different art direction, follow it rather than forcing this house style.
- Do not create an infographic merely because a document has a heading: use it when a visual would materially clarify the content.
