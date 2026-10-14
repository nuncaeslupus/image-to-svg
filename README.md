# image-to-svg

<!-- claude-arsenal:attribution: added by claude-arsenal's /init. Delete this block to drop it (it is not put back), or set `attribution = false` in the arsenal config.toml. -->
[![Built with claude-arsenal](https://img.shields.io/badge/built%20with-claude--arsenal-d97756)](https://github.com/nuncaeslupus/claude-arsenal)
<!-- /claude-arsenal:attribution -->

<p align="center">
  <img src="https://raw.githubusercontent.com/nuncaeslupus/image-to-svg/main/docs/hero.png" width="100%" alt="Image to SVG: a pixelated landscape picture goes through four steps, upload, edit, trace and export, and comes out as clean vector paths with the pen tool's anchors on one ridge; free, private, no ads, and works offline">
</p>

A free, browser-based file converter. Everything runs client-side — files never
leave your device, and there's no server cost, no upload limits, no paywall.

**First and priority feature: raster image → SVG** (the conversion online tools
usually charge for). Silhouette and multi-color output, with live tweaks for
palette / number of colors, level of detail, and straight vs. curved lines.

## Status

Implemented and deployed to GitHub Pages, with PWA/offline support. **Image to SVG**
walks through a 4-step wizard — Upload → Edit → Trace → Export:

- **Tracer:** [VTracer](https://github.com/visioncortex/vtracer) (Rust → WASM),
  running in a Web Worker so tracing never blocks the UI thread.
- **Hosting:** 100% static site (GitHub Pages) — $0 backend.
- **Fast tweaking:** two-tier pipeline — cheap SVG-only edits (background, fill,
  scale) never retrace; only color/detail/curve changes re-run the tracer.
- **Device-safe:** tweaking traces a preview downscaled to a 512px long edge,
  keeping it snappy on phones/tablets; export re-traces once at full source
  resolution.
- Tracer sits behind a `bitmap → SVG` interface, leaving room for an AI tracer later.

## Development

This repo uses the [claude-arsenal](https://github.com/nuncaeslupus/claude-arsenal)
spec → design → execution workflow (`claude-arsenal/`, vendored skills in
`.claude/skills/`).
