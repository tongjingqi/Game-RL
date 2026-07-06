# GameQA Example Viewer

Local browser for the repository's `src/*/*dataset_example/data.json` files.

```bash
python tools/gameqa_viewer/server.py
```

Then open `http://127.0.0.1:8765/`.

The server scans every example dataset at startup, normalizes the common `options` / `Options` field difference, serves referenced images and states, and keeps raw sample JSON visible for schema checks.

## UI features

- **Filters**: game, task, difficulty (`qa_level`), plot level, plus free-text search across id / description / question / answer previews; one-click reset.
- **Answer highlighting**: for multiple-choice samples the correct option is marked with a ✓ badge, and the answer block shows the resolved option text.
- **Image zoom**: click the board image to open a full-screen lightbox; "Open original" serves the raw file.
- **JSON tools**: state and raw-sample JSON with syntax highlighting and one-click copy.
- **Light / dark theme**: toggle in the top bar (follows system preference by default, persisted in `localStorage`).
- **Shareable URLs**: current game + sample are kept in the query string (`?game=...&sample=...`).

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `←` / `→` | Previous / next sample (respects active filters) |
| `/` | Focus the search box |
| `Esc` | Close the image lightbox |
