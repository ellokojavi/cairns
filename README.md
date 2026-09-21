# Enchantments traverse — Jo, Juanjo, Javier — Sept 22, 2026

Installable offline hike planner. Works with no signal; GPS keeps working because
position comes from satellites, not the network.

## Publish (one time, ~5 minutes)

1. Create a new **public** repository on GitHub, e.g. `enchantments`.
2. Upload every file in this folder to the repository root:
   `index.html`, `sw.js`, `manifest.webmanifest`, `icon-192.png`, `icon-512.png`, `.nojekyll`
3. Repository **Settings → Pages** → Source: **Deploy from a branch**,
   Branch: **main**, Folder: **/ (root)** → Save.
4. Wait 1–2 minutes. The page appears at
   `https://<your-username>.github.io/enchantments/`

`.nojekyll` matters: without it GitHub Pages runs Jekyll, which can mangle files.

## Install on a phone

**Android (Chrome):** open the link → menu (⋮) → *Add to Home screen* / *Install app*.
**iOS (Safari — must be Safari):** open the link → Share → *Add to Home Screen*.

Wait until the strip at the top of the page reads **"Saved for offline"** before
leaving signal. That is the confirmation the page has stored itself.

## Files

| File | Purpose |
|---|---|
| `index.html` | The whole planner: route, map, elevation, schedule, intake, GPS |
| `sw.js` | Service worker — stores the page for offline use |
| `manifest.webmanifest` | Makes it installable as an app |
| `icon-192.png`, `icon-512.png` | Home screen icons |
| `.nojekyll` | Stops GitHub Pages from processing the files |
