"""GraphCraft path constants."""

from pathlib import Path

GRAPHCRAFT_OUT = Path("graphcraft-out")
DESIGN_GRAPH_JSON = GRAPHCRAFT_OUT / "design-graph.json"
DESIGN_REPORT = GRAPHCRAFT_OUT / "DESIGN_REPORT.md"
BRIDGE_JSON = GRAPHCRAFT_OUT / "bridge.json"

DESIGN_SYSTEM_DIR = Path("design-system")
DESIGN_SCREENS_DIR = Path("design") / "screens"
DESIGN_COMPONENTS_DIR = DESIGN_SYSTEM_DIR / "components"
STYLES_DIR = Path("packs") / "styles"
STITCH_DIR = Path(".stitch")
CONFIG_FILE = Path("graphcraft.config.yaml")

HANDOFF_AESTHETIC = Path("handoff") / "AESTHETIC_BRIEF.md"
HANDOFF_DESIGN = Path("handoff") / "DESIGN_BRIEF.md"

PACKAGES_UI = Path("packages") / "ui-core"
PACKAGES_ASSETS = Path("packages") / "assets"
