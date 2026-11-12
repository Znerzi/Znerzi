"""Validate the committed SVG assets used by the profile README.

The SVG files are intentionally committed so GitHub can render the profile
without running a build step. This script verifies that every required asset
is present, is valid SVG, and is referenced by the README under the right name.
"""

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ROOT / "assets"
README = ROOT / "README.md"

REQUIRED_ASSETS = (
    "hero.svg",
    "t-about.svg",
    "about.svg",
    "t-stack.svg",
    "s-frontend.svg",
    "s-backend.svg",
    "s-tools.svg",
    "s-cloud.svg",
    "s-additional.svg",
    "s-services.svg",
    "t-work.svg",
    "project-csnk.svg",
    "project-webimix.svg",
    "project-merlarchive.svg",
    "project-portfolio.svg",
    "t-activity.svg",
    "activity-public.svg",
    "activity-contrib.svg",
    "activity-profile.svg",
    "contact.svg",
)


def validate_svg(path: Path) -> list[str]:
    errors = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        return [f"{path.name}: invalid XML ({error})"]

    if not root.tag.endswith("svg"):
        errors.append(f"{path.name}: root element is not <svg>")
    if not root.get("viewBox"):
        errors.append(f"{path.name}: missing viewBox")
    return errors


def main() -> int:
    errors = []
    readme_text = README.read_text(encoding="utf-8")

    for name in REQUIRED_ASSETS:
        path = ASSET_DIR / name
        if not path.is_file():
            errors.append(f"Missing asset: assets/{name}")
            continue
        errors.extend(validate_svg(path))
        if f"./assets/{name}" not in readme_text:
            errors.append(f"README does not reference assets/{name}")

    local_sources = re.findall(r'src="\./([^"?]+)', readme_text)
    for source in local_sources:
        if not (ROOT / source).is_file():
            errors.append(f"README references missing file: {source}")

    if errors:
        print("Asset validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Asset validation passed: {len(REQUIRED_ASSETS)} SVG files are ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
