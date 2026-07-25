/**
 * Generates the PWA / home-screen icons from the app's logo mark, so the
 * install prompt and installed icon match the in-app LogoMark and favicon.
 *
 * A white pen-tool mark (Bézier curve between two square anchors) on the brand
 * teal — the same mark as src/components/shellIcons.tsx LogoMark and
 * public/favicon.svg. "any" icons are a rounded squircle; the maskable icon is
 * full-bleed with the mark kept inside the safe zone (Android masks it to
 * arbitrary shapes).
 *
 * The generated PNGs are COMMITTED (public/pwa-*.png), so resvg is NOT a
 * committed dependency (a native binary that would bloat every CI install).
 * Install it ad-hoc only when regenerating:
 *
 *   npm i -D @resvg/resvg-js && node scripts/generate-icons.mjs && npm uninstall @resvg/resvg-js
 *
 * Keep ACCENT + MARK in sync with public/favicon.svg / the LogoMark.
 */
import { writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

let Resvg;
try {
  ({ Resvg } = await import("@resvg/resvg-js"));
} catch {
  throw new Error(
    "@resvg/resvg-js is not installed — it's not a committed dependency (the icons are). " +
      "Install it ad-hoc to regenerate: npm i -D @resvg/resvg-js && node scripts/generate-icons.mjs",
  );
}

const OUT_DIR = resolve(dirname(fileURLToPath(import.meta.url)), "..", "public");
const ACCENT = "#0e8f86";
const SIZE = 512;

// The mark, white, in its native 40×40 space (mirrors favicon.svg / LogoMark).
const MARK = `
  <path d="M9 27 C 21 27, 13 13, 31 13" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/>
  <rect x="5.5" y="23.5" width="7" height="7" rx="1.3" fill="#fff"/>
  <rect x="27.5" y="9.5" width="7" height="7" rx="1.3" fill="#fff"/>`;

/** markPct = fraction of the canvas the 40×40 mark spans; bleed = full-square
 * background (maskable) vs a rounded squircle (any). */
function iconSvg({ markPct, bleed }) {
  const mark = SIZE * markPct;
  const scale = mark / 40;
  const off = (SIZE - mark) / 2;
  const bg = bleed
    ? `<rect width="${SIZE}" height="${SIZE}" fill="${ACCENT}"/>`
    : `<rect width="${SIZE}" height="${SIZE}" rx="112" ry="112" fill="${ACCENT}"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${SIZE}" height="${SIZE}" viewBox="0 0 ${SIZE} ${SIZE}">
    ${bg}
    <g transform="translate(${off} ${off}) scale(${scale})">${MARK}</g>
  </svg>`;
}

const anySvg = iconSvg({ markPct: 0.56, bleed: false });
const maskableSvg = iconSvg({ markPct: 0.46, bleed: true }); // smaller: Android safe zone

const targets = [
  { svg: anySvg, width: 192, file: "pwa-192x192.png" },
  { svg: anySvg, width: 512, file: "pwa-512x512.png" },
  { svg: maskableSvg, width: 512, file: "pwa-maskable-512x512.png" },
];

for (const { svg, width, file } of targets) {
  const png = new Resvg(svg, { fitTo: { mode: "width", value: width } }).render().asPng();
  const out = resolve(OUT_DIR, file);
  writeFileSync(out, png);
  console.log(`wrote ${out} (${(png.length / 1024).toFixed(1)} KB)`);
}
