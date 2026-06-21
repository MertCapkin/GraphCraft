/**
 * Export Stitch project screens to GraphCraft .stitch/ layout.
 * Run via: npx -y -p @google/stitch-sdk node pull_export.mjs --project ID --out DIR
 *
 * Requires STITCH_API_KEY (or STITCH_ACCESS_TOKEN + GOOGLE_CLOUD_PROJECT).
 */
import { stitch } from "@google/stitch-sdk";
import fs from "node:fs";
import path from "node:path";

function parseArgs(argv) {
  const out = { project: "", out: "", html: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--project" && argv[i + 1]) out.project = argv[++i];
    else if (a === "--out" && argv[i + 1]) out.out = argv[++i];
    else if (a === "--html") out.html = true;
  }
  return out;
}

function screenKey(screen, index) {
  const raw =
    screen.name ||
    screen.title ||
    screen.screenId ||
    screen.id ||
    `screen-${index}`;
  const slug = String(raw)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || `screen-${index}`;
}

async function downloadUrl(url, dest) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Download failed ${res.status}: ${url}`);
  }
  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(dest, buf);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (!args.project || !args.out) {
    console.error(
      "Usage: node pull_export.mjs --project <stitch-project-id> --out <export-dir> [--html]",
    );
    process.exit(2);
  }

  if (
    !process.env.STITCH_API_KEY &&
    !(process.env.STITCH_ACCESS_TOKEN && process.env.GOOGLE_CLOUD_PROJECT)
  ) {
    console.error(
      "Missing auth: set STITCH_API_KEY or STITCH_ACCESS_TOKEN + GOOGLE_CLOUD_PROJECT",
    );
    process.exit(3);
  }

  const outDir = path.resolve(args.out);
  const designsDir = path.join(outDir, "designs");
  fs.mkdirSync(designsDir, { recursive: true });

  const project = stitch.project(args.project);
  const screens = await project.screens();

  const screensMeta = {};
  const designLines = [
    "# Stitch Design",
    "",
    `Project: ${args.project}`,
    "",
    "## Screens",
    "",
  ];

  for (let i = 0; i < screens.length; i++) {
    const screen = screens[i];
    const key = screenKey(screen, i);
    const stitchId = String(screen.screenId || screen.id || key);
    const label =
      screen.title || screen.name || stitchId.replace(/_/g, " ");

    const imageUrl = await screen.getImage();
    const pngName = `${key}.png`;
    await downloadUrl(imageUrl, path.join(designsDir, pngName));

    const entry = {
      id: `screen:${key}`,
      title: label,
      png: pngName,
      stitch_screen_id: stitchId,
      status: "imported",
    };

    if (args.html) {
      try {
        const htmlUrl = await screen.getHtml();
        const htmlName = `${key}.html`;
        await downloadUrl(htmlUrl, path.join(designsDir, htmlName));
        entry.html = htmlName;
      } catch (err) {
        entry.html_error = String(err?.message || err);
      }
    }

    screensMeta[key] = entry;
    designLines.push(`- **${label}** (\`${entry.id}\`) — \`${pngName}\``);
  }

  let designSystems = [];
  try {
    designSystems = await project.listDesignSystems();
    if (designSystems.length) {
      designLines.push("", "## Design systems", "");
      for (const ds of designSystems) {
        const dsId = ds.assetId || ds.id || "unknown";
        designLines.push(`- ${dsId}`);
      }
    }
  } catch {
    // optional — not all projects expose design systems
  }

  const metadata = {
    project_id: args.project,
    screens: screensMeta,
    flows: [],
    source: "graphcraft-stitch-pull",
    screen_count: screens.length,
  };

  fs.writeFileSync(
    path.join(outDir, "metadata.json"),
    JSON.stringify(metadata, null, 2) + "\n",
    "utf8",
  );
  fs.writeFileSync(
    path.join(outDir, "DESIGN.md"),
    designLines.join("\n") + "\n",
    "utf8",
  );

  const summary = {
    ok: true,
    project_id: args.project,
    screens: screens.length,
    export_dir: outDir,
    design_systems: designSystems.length,
  };
  console.log(JSON.stringify(summary));
}

main().catch((err) => {
  const payload = {
    ok: false,
    error: String(err?.message || err),
    code: err?.code || "PULL_FAILED",
  };
  console.error(JSON.stringify(payload));
  process.exit(1);
});
