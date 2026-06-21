"""GraphCraft path constants."""

from pathlib import Path

GRAPHCRAFT_OUT = Path("graphcraft-out")
DESIGN_GRAPH_JSON = GRAPHCRAFT_OUT / "design-graph.json"
DESIGN_REPORT = GRAPHCRAFT_OUT / "DESIGN_REPORT.md"
BRIDGE_JSON = GRAPHCRAFT_OUT / "bridge.json"
AESTHETIC_REPORT = GRAPHCRAFT_OUT / "AESTHETIC_REPORT.md"
VISUAL_REVIEW_REPORT = GRAPHCRAFT_OUT / "VISUAL_REVIEW.md"
STITCH_REPORT = GRAPHCRAFT_OUT / "STITCH_REPORT.md"

DESIGN_SYSTEM_DIR = Path("design-system")
DESIGN_SCREENS_DIR = Path("design") / "screens"
DESIGN_COMPONENTS_DIR = DESIGN_SYSTEM_DIR / "components"
STYLES_DIR = Path("packs") / "styles"
STITCH_DIR = Path(".stitch")
CONFIG_FILE = Path("graphcraft.config.yaml")

HANDOFF_AESTHETIC = Path("handoff") / "AESTHETIC_BRIEF.md"
HANDOFF_DESIGN = Path("handoff") / "DESIGN_BRIEF.md"
RESEARCH_INSPIRATION = Path("research") / "INSPIRATION.md"
DESIGN_STATE_JSON = Path("handoff") / "DESIGN_STATE.json"
DESIGN_GATE_OFF_FILE = Path("handoff") / ".design-gate-off"

HANDOFF_DIR = Path("handoff")
STATE_JSON = HANDOFF_DIR / "STATE.json"
DOING_DIR = HANDOFF_DIR / "board" / "doing"

PACKAGES_UI = Path("packages") / "ui-core"
PACKAGES_ASSETS = Path("packages") / "assets"
