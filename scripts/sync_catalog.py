#!/usr/bin/env python3
"""Regenerate the APM packages under packs/ from a Packy Catalog checkout.

Usage: scripts/sync_catalog.py [path/to/packy-catalog]

Each Catalog Pack becomes one APM package at packs/<pack-id>/. A Pack whose
Claude skill variants differ from its Agents variants also gets a
packs/<pack-id>-claude/ package carrying the Claude variants.
"""

import filecmp
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OWNER = "yersonargotev"
REPO_SLUG = f"{OWNER}/skills"


def same_tree(a: Path, b: Path) -> bool:
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    if mismatch or errors:
        return False
    return all(same_tree(a / d, b / d) for d in cmp.common_dirs)


def source_for(resource: dict, surface: str) -> str:
    for variant in resource.get("variants", []):
        if variant["surface"] == surface:
            return variant["source"]
    return resource["source"]


def surfaces_of(resource: dict) -> list:
    return [b["surface"] for b in resource["bindings"]]


def required_assets(resource: dict) -> set:
    ids = {r.split(":", 1)[1] for r in resource.get("requires", []) if r.startswith("asset:")}
    for variant in resource.get("variants", []):
        ids |= {r.split(":", 1)[1] for r in variant.get("requires", []) if r.startswith("asset:")}
    for binding in resource["bindings"]:
        for cap in binding.get("capabilities", []):
            for ref in cap.get("claude_composite_skill", {}).get("references", []):
                if ref["kind"] == "asset":
                    ids.add(ref["id"])
    return ids


def yaml_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def write_package(pack: dict, src: Path, name: str, surface: str, note: str) -> dict:
    dest = REPO / "packs" / name
    resources = pack["resources"]
    assets = {r["id"]: r for r in resources if r["kind"] == "asset"}
    skills = []

    for res in resources:
        kind = res["kind"]
        if kind == "skill":
            bound = surfaces_of(res)
            if surface == "claude" and "claude" not in bound:
                continue
            use = surface if surface in bound else bound[0]
            out = dest / "skills" / res["id"]
            shutil.copytree(src / source_for(res, use), out)
            for asset_id in sorted(required_assets(res)):
                asset_src = src / assets[asset_id]["source"]
                target = out / "references" / asset_src.name
                if target.exists():
                    if filecmp.cmp(asset_src, target, shallow=False):
                        continue
                    raise SystemExit(f"{name}: {target} differs from asset {asset_id}")
                target.parent.mkdir(exist_ok=True)
                shutil.copy2(asset_src, target)
            skills.append(res["id"])
        elif kind == "agent":
            out = dest / ".apm" / "agents" / f"{res['id']}.agent.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src / res["source"], out)
        elif kind == "instruction":
            out = dest / ".apm" / "instructions" / f"{res['id']}.instructions.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            body = (src / res["source"]).read_text()
            front = f'---\ndescription: {yaml_str(res["description"])}\napplyTo: "**"\n---\n\n'
            out.write_text(front + body)
        elif kind == "notice":
            out = dest / "notices" / Path(res["source"]).name
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src / res["source"], out)

    licenses = sorted({r["license"] for r in resources if r["kind"] == "notice" and r.get("license")})
    description = pack["description"] + note
    lines = [
        f"name: {name}",
        f"version: {pack['version']}",
        f"description: {yaml_str(description)}",
        f"author: {OWNER}",
    ]
    if licenses:
        lines.append(f"license: {yaml_str(' AND '.join(licenses))}")
    lines.append("x-packy:")
    lines.append(f"  pack: {pack['id']}")
    lines.append(f"  surface: {surface}")
    if pack["origins"]:
        lines.append("  origins:")
        for origin in pack["origins"]:
            lines.append(f"    - repository: {origin['repository']}")
            lines.append(f"      commit: {origin['commit']}")
    if pack.get("external_requirements"):
        lines.append(f"  external_requirements: {json.dumps(pack['external_requirements'])}")
    (dest / "apm.yml").write_text("\n".join(lines) + "\n")

    return {"name": name, "version": pack["version"], "description": description, "skills": sorted(skills)}


def main() -> None:
    catalog = Path(sys.argv[1] if len(sys.argv) > 1 else REPO.parent / "packy-catalog").resolve()
    packs_dir = REPO / "packs"
    if packs_dir.exists():
        shutil.rmtree(packs_dir)

    packages = []
    for manifest in sorted(catalog.glob("packs/*/pack.json")):
        pack = json.loads(manifest.read_text())
        src = manifest.parent
        differs = any(
            r["kind"] == "skill"
            and {"agents", "claude"} <= set(surfaces_of(r))
            and not same_tree(src / source_for(r, "agents"), src / source_for(r, "claude"))
            for r in pack["resources"]
        )
        note = " (Agents variants; use the -claude package for Claude Code)" if differs else ""
        packages.append(write_package(pack, src, pack["id"], "agents", note))
        if differs:
            packages.append(write_package(pack, src, f"{pack['id']}-claude", "claude", " (Claude Code variants)"))

    root = [
        "name: skills",
        "version: 1.0.0",
        f"description: {yaml_str('Reviewed agent skill packs from the Packy Catalog, packaged for APM')}",
        f"author: {OWNER}",
        "marketplace:",
        "  owner:",
        f"    name: {OWNER}",
        f"    url: https://github.com/{OWNER}",
        "  packages:",
    ]
    for pkg in packages:
        root += [
            f"    - name: {pkg['name']}",
            f"      description: {yaml_str(pkg['description'])}",
            f"      source: ./packs/{pkg['name']}",
            f"      version: {pkg['version']}",
        ]
    (REPO / "apm.yml").write_text("\n".join(root) + "\n")

    table = ["| Package | Version | Skills | Description |", "| --- | --- | --- | --- |"]
    for pkg in packages:
        table.append(f"| [`{pkg['name']}`](packs/{pkg['name']}) | {pkg['version']} | {len(pkg['skills'])} | {pkg['description']} |")
    readme = (REPO / "README.md").read_text()
    start, end = "<!-- packages:start -->", "<!-- packages:end -->"
    head, rest = readme.split(start)
    tail = rest.split(end)[1]
    (REPO / "README.md").write_text(head + start + "\n" + "\n".join(table) + "\n" + end + tail)

    total = sum(len(p["skills"]) for p in packages)
    print(f"{len(packages)} packages, {total} skills from {catalog}")


if __name__ == "__main__":
    main()
