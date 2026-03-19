---
name: pmf-change-logo
description: >
  Replace the app logo in the design guide .pen file.
  Triggers when the user asks to change, replace, or update the logo,
  app icon, or brand mark in the Pencil design guide.
user-invocable: true
metadata:
  version: "1.0.2"
  category: design
  type: unit
  style: procedural
  triggers: [change logo, replace logo, update app icon, brand mark, app logo]
  uses: []
---

# Change Logo

Replace the logo component in the design guide.

## Logo Specifications

- **Shape**: Square (recommended 192x192)
- **Background**: Transparent or app Primary color
- **Placement**: Reusable component named `Logo` -- all instances update simultaneously

## Step 1 -- Verify Current File

```
mcp__pencil__get_editor_state()
```

Verify that the currently open `.pen` file is the app design guide.
If it is `material-design-guide.lib.pen`, instruct the user to open the app-specific file.

## Step 2 -- Determine Logo Source

Ask the user:

- **Image file path provided** -- Apply the image as a fill
- **AI generation requested** -- Generate an AI logo based on the app name
- **Text/initials only** -- Generate a text-based logo

## Step 3 -- Find Logo Node

```
mcp__pencil__batch_get(patterns=["Logo"])
```

Find the node ID of the reusable component named `Logo`.

- If node does not exist: Create a new 192x192 reusable frame `Logo` using `mcp__pencil__batch_design`
- If node exists but has no inner image node: Add a 192x192 Rectangle + image fill node inside the existing Logo frame using `batch_design`
- If node exists and inner image node also exists: Use that node ID

## Step 4 -- Replace Logo

### Case A: AI Generation

```
G(<logoNodeId>, "ai", "<appname> app logo square minimal")
```

### Case B: Image File

> SVG files cannot be applied directly as Pencil image fills (they render as transparent).
> Convert to PNG/JPG before use:
> - macOS: `sips -s format png logo.svg --out logo.png`
> - Linux/Windows: `python3 -c "from PIL import Image; Image.open('logo.svg').save('logo.png')"`
>   (requires `pip install Pillow`)
> - ImageMagick (cross-platform): `convert logo.svg logo.png`

```
mcp__pencil__batch_design
U(<logoNodeId>, { fill: { type: "image", url: "<file_path>" } })
```

### Case C: Text Initials

```
mcp__pencil__batch_design
bg=I(<logoNodeId>, { type: "frame", width: "fill_container", height: "fill_container", fill: "$primary" })
label=I(<logoNodeId>, { type: "text", content: "<initials>", fontSize: 72, fill: "$onPrimary", textAlign: "center" })
```

## Step 5 -- Verify Result

```
mcp__pencil__get_screenshot(<logoNodeId>)
```

Verify the result via screenshot and show it to the user.
If unsatisfactory, return to Step 4 and retry.
