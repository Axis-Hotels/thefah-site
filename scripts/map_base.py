#!/usr/bin/env python3
"""Draw the Silom neighbourhood base map (docs/img/silom-map.svg) from OpenStreetMap data.

Run only when the area changes:
  python3 scripts/map_base.py <folder with *.osm files from api.openstreetmap.org/api/0.6/map>

Map data © OpenStreetMap contributors, ODbL. The projection constants are shared with build.py
(content/map.json) so the interactive points line up with the drawing.
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = json.loads((ROOT / "content/map.json").read_text(encoding="utf-8"))
W, H = MAP["width"], MAP["height"]
W_LON, E_LON, S_LAT, N_LAT = MAP["west"], MAP["east"], MAP["south"], MAP["north"]


def xy(lat, lon):
    return ((lon - W_LON) / (E_LON - W_LON) * W, (N_LAT - lat) / (N_LAT - S_LAT) * H)


def load(folder):
    nodes, ways = {}, {}
    for f in sorted(Path(folder).glob("*.osm")):
        root = ET.parse(f).getroot()
        for n in root.iter("node"):
            nodes[n.get("id")] = (float(n.get("lat")), float(n.get("lon")))
        for w in root.iter("way"):
            tags = {t.get("k"): t.get("v") for t in w.iter("tag")}
            ways[w.get("id")] = ([nd.get("ref") for nd in w.iter("nd")], tags)
    return nodes, ways


def path_d(refs, nodes, close=False, prec=1):
    pts = [xy(*nodes[r]) for r in refs if r in nodes]
    if len(pts) < 2:
        return ""
    # drop points closer than ~1 unit to keep the file small
    out = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) >= 1.2:
            out.append(p)
    if len(out) < 2:
        return ""
    fmt = lambda v: f"{v:.{prec}f}".rstrip("0").rstrip(".")
    d = "M" + " L".join(f"{fmt(x)} {fmt(y)}" for x, y in out)
    return d + ("Z" if close else "")


def bbox_ok(refs, nodes):
    for r in refs:
        if r in nodes:
            x, y = xy(*nodes[r])
            if -50 <= x <= W + 50 and -50 <= y <= H + 50:
                return True
    return False


def area(refs, nodes):
    pts = [xy(*nodes[r]) for r in refs if r in nodes]
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2


ROAD_CLASSES = {
    "major": {"motorway", "trunk", "primary", "secondary"},
    "minor": {"tertiary", "unclassified", "residential", "living_street"},
    "lane": {"service", "pedestrian"},
}


def main(folder):
    nodes, ways = load(folder)
    layers = {k: [] for k in ("park", "water", "building", "lane", "minor", "major", "expressway", "bts", "mrt")}
    for refs, tags in ways.values():
        if not bbox_ok(refs, nodes):
            continue
        hw, rw = tags.get("highway"), tags.get("railway")
        if tags.get("leisure") == "park" or tags.get("landuse") in ("grass",) and area(refs, nodes) > 400:
            layers["park"].append(path_d(refs, nodes, True))
        elif tags.get("natural") == "water" or tags.get("waterway") in ("canal", "river"):
            layers["water"].append(path_d(refs, nodes, tags.get("natural") == "water"))
        elif "building" in tags and area(refs, nodes) > 60:
            layers["building"].append(path_d(refs, nodes, True))
        elif hw:
            if hw == "motorway" or tags.get("bridge") == "yes" and hw in ("motorway", "trunk", "motorway_link"):
                layers["expressway"].append(path_d(refs, nodes))
            else:
                for cls, kinds in ROAD_CLASSES.items():
                    if hw in kinds:
                        layers[cls].append(path_d(refs, nodes))
        elif rw in ("subway", "light_rail", "rail", "monorail") and tags.get("service") not in ("yard", "siding", "spur"):
            name = " ".join(tags.get(k, "") for k in ("name", "name:en", "network", "operator")).lower()
            if "bts" in name or "บีทีเอส" in name or "ระบบขนส่งมวลชนกรุงเทพ" in name:
                layers["bts"].append(path_d(refs, nodes))
            else:
                layers["mrt"].append(path_d(refs, nodes))

    style = {
        "park": 'fill="#CFE0C3"',
        "water": 'fill="#BFD6EA" stroke="#BFD6EA" stroke-width="3"',
        "building": 'fill="#E2E7EC"',
        "lane": 'fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"',
        "minor": 'fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"',
        "major": 'fill="none" stroke="#FFFFFF" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"',
        "expressway": 'fill="none" stroke="#D3DBE3" stroke-width="7" stroke-linecap="round"',
        "bts": 'fill="none" stroke="#2E8B57" stroke-width="3.2" stroke-linecap="round" opacity=".9"',
        "mrt": 'fill="none" stroke="#2F5DA8" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="7 6" opacity=".85"',
    }
    vx, vy, vw, vh = MAP.get("view", [0, 0, W, H])
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {vw} {vh}" width="{vw}" height="{vh}">',
             f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="#F1F3F2"/>']
    for name in ("park", "water", "building", "lane", "minor", "major", "expressway", "bts", "mrt"):
        ds = [d for d in layers[name] if d]
        if ds:
            parts.append(f'<path {style[name]} d="{" ".join(ds)}"/>')
    parts.append("</svg>\n")
    out = ROOT / "docs/img/silom-map.svg"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(out, out.stat().st_size // 1024, "KB", {k: len(v) for k, v in layers.items()})


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
