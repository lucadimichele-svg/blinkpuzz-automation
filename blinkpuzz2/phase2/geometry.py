"""Audit the geometry submitted to the renderer against the public game, in model units."""

import math

from blinkpuzz2.core import require

from . import objects, sets
from .experience import SAFE
from .stage import Stage, grid, grid_pose, offset

BUILDERS = {
    "laser": sets.optic,
    "maze": sets.maze,
    "pipes": sets.pipes,
    "gears": sets.gears,
    "search": objects.search,
    "mismatch": objects.mismatch,
    "fit": objects.fit,
    "shadow": objects.shadow,
}


def build_scene(s):
    st = Stage(s)
    BUILDERS[s.family](st, s)
    return st


def close(a, b, tol=0.08):
    require(math.dist(a, b) < tol, "Displayed geometry displaced")


def check_scene(s, st):
    b = s.board
    f = s.family
    tagged = [n for n in st.nodes if n.get("tag")]
    by = {n["tag"]: n for n in tagged}
    require(len(by) == len(tagged), "Duplicate visible entity")
    if f == "laser":
        pitch = grid_pose(s)[2]
        for x, y, mirror in b["mirrors"]:
            n = by[f"mirror-{x}-{y}"]
            close(n["pos"], grid(s, st, x, y, 38))
            expected = grid_pose(s)[3] + (-45 if mirror == "/" else 45)
            require(
                abs((n["angle"] - expected + 90) % 180 - 90) < 0.01
                and abs(n["size"][0] - pitch * 0.68 * math.sqrt(2)) < 0.01,
                "Mirror normal or length differs",
            )
        start = grid(s, st, -0.62, b["emitter_row"], 30)
        end = grid(s, st, -0.20, b["emitter_row"], 34)
        close(by["emitter"]["pos"], [(x + y) / 2 for x, y in zip(start, end)])
        for i, p in enumerate(b["receivers"]):
            n = by[f"receiver-{i}"]
            close(n["pos"], grid(s, st, *p, 57))
            require(len(n["outline"]) == (3, 4, 6)[i], "Wrong receiver shape")
        require(len(by) == len(b["mirrors"]) + 4, "Extra optical component")
    elif f == "maze":
        n = b["size"]
        walls = set()
        pitch = grid_pose(s)[2]
        # Reconstruct corridor and gate openings from endpoints of the actual wall meshes.
        for x in range(n):
            for y in range(n):
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + dx, y + dy)
                    if q[0] < 0 and [x, y] in b["entrances"] or q[0] >= n and [x, y] == b["exit"]:
                        continue
                    if any({(x, y), q} == {tuple(a), tuple(z)} for a, z in b["passages"]):
                        continue
                    mid = grid(s, st, x + 0.5 * dx, y + 0.5 * dy, 49)
                    walls.add(tuple(round(v, 2) for v in mid))
                    hits = [v for v in tagged if math.dist(v["pos"], mid) < 0.05]
                    require(
                        len(hits) == 1 and abs(hits[0]["size"][0] - pitch) < 0.01,
                        "Missing or misplaced wall",
                    )
                    angle = grid_pose(s)[3] + (90 if dx else 0)
                    require(abs((hits[0]["angle"] - angle + 90) % 180 - 90) < 0.01, "Rotated wall")
        require(len(walls) == len(tagged), "Unexpected passage obstruction")
    elif f == "gears":
        for x, y in b["wheels"]:
            n = by[f"gear-{x}-{y}"]
            close(n["pos"], grid(s, st, x, y, 54))
            radii = [math.hypot(*q) for q in n["outline"]]
            require(
                abs(max(radii) - 79) < 0.01 and abs(min(radii) - 0.88 * 79) < 0.01,
                "Bad pitch diameter",
            )
            require(
                (n["mat"] == "red") == ([x, y] == b["output"])
                and (n["mat"] == "turquoise") == ([x, y] == b["drive"]),
                "Wrong output or drive",
            )
        require(len(by) == len(b["wheels"]), "Unexpected wheel")
    elif f == "pipes":
        from blinkpuzz2.engines.pipes import PORTS

        r = grid_pose(s)[2] / 2

        def ports(node, p, tile):
            actual = [node["points"][0], node["points"][-1]]
            for d in tile:
                dx, dy = PORTS[d]
                end = [p[0] + dx * r, p[1] + dy * r, p[2]]
                require(
                    any(math.dist(a, end) < 0.05 for a in actual), "Rendered pipe port mismatch"
                )

        for y, row in enumerate(b["grid"]):
            for x, t in enumerate(row):
                if t != "?":
                    ports(by[f"pipe-{x}-{y}"], grid(s, st, x, y, 41), t)
                else:
                    require(f"pipe-{x}-{y}" not in by, "Socket obstructed")
        for i, t in enumerate(b["pieces"]):
            ports(by[f"spare-geometry-{i}"], st.floor(252 + 249 * i, 1383, 40), t)
        require(len(by) == sum(map(len, b["grid"])) + 2, "Extra connector")
    elif f == "search":
        bounds = []
        for i, (wing, spots, dx, dy, angle) in enumerate(
            [*b["specimens"], [*b["sample"], 0, 0, 0]]
        ):
            tag = f"moth-{i}" if i < len(b["specimens"]) else "sample"
            for side in ("left", "right"):
                n = by[f"{tag}-{side}"]
                require(len(n["outline"]) == (8, 9, 10)[wing], "Wing contour differs")
            for side in (-1, 1):
                require(
                    sum(k.startswith(f"{tag}-spot-{side}-") for k in by) == spots, "Eyespots differ"
                )
            # Check the projected union of both forewings, including rotation and the specimen's physical height.
            points = [
                st.screen([n["pos"][0] + u, n["pos"][1] + v, n["pos"][2]])
                for n in [by[tag + "-left"], by[tag + "-right"]]
                for u, v in n["outline"]
            ]
            box = [
                min(p[0] for p in points) - 3,
                min(p[1] for p in points) - 3,
                max(p[0] for p in points) + 3,
                max(p[1] for p in points) + 42,
            ]
            for a, c, z, d in bounds:
                require(
                    min(z, box[2]) <= max(a, box[0]) or min(d, box[3]) <= max(c, box[1]),
                    "Occluded specimen",
                )
            bounds.append(box)
    elif f == "mismatch":
        for j, bank in enumerate(("upper", "lower")):
            for i, (kind, v) in enumerate(b[bank]):
                cols = b["layout"][0]
                x = 161 + (i % cols + 0.5) * 680 / cols
                p = st.floor(x, (766, 1242)[j] - 94 + i // cols * 119, 50)
                n = by[f"{bank}-{i}"]
                if kind == "dial":
                    dx = n["points"][-1][0] - p[0]
                    dy = n["points"][-1][1] - p[1]
                    require(
                        abs(math.degrees(math.atan2(dy, dx)) - (-145, -90, -35)[v]) < 0.05,
                        "Wrong dial angle",
                    )
                else:
                    close(
                        n["pos"],
                        [
                            p[0] + (v - 1) * (27 if kind == "lever" else 30),
                            p[1] - (14 if kind == "lever" else 0),
                            p[2] + (40 if kind == "lever" else 14),
                        ],
                    )
    elif f == "fit":
        for points, bits, r in [
            (by["die"]["hole"], b["socket"], 85),
            *[(by[f"insert-{i}"]["outline"], v, 85) for i, v in enumerate(b["parts"])],
        ]:
            require(len(points) == 6 * len(bits), "Invalid broach mesh")
            decoded = [int(math.hypot(*points[6 * i + 2]) > 1.17 * r) for i in range(len(bits))]
            require(decoded == bits, "Socket teeth disagree with public profile")
            for i, (x, y) in enumerate(points):
                slot, corner = divmod(i, 6)
                fraction = (0, 0.13, 0.18, 0.73, 0.78, 0.99)[corner]
                angle = (slot + fraction) * math.tau / len(bits) - math.pi / 2
                radius = r * (1 + 0.34 * (corner in (2, 3)) * bits[slot])
                close([x, y], [radius * math.cos(angle), radius * math.sin(angle)])
    else:
        for i, tower in enumerate(b["towers"]):
            for row, heights in enumerate(tower):
                for col, h in enumerate(heights):
                    vox = [n for k, n in by.items() if k.startswith(f"voxel-{i}-{row}-{col}-")]
                    require(len(vox) == h, "Sculpture geometry differs from projection model")
                    cx, cy, unit = objects.tower_layout(i, len(heights))
                    yaw = math.radians(-15)
                    dx = (col - (len(heights) - 1) / 2) * unit
                    dy = (0.5 - row) * unit
                    foot = st.floor(cx, cy, 36)
                    for z in range(h):
                        node = by[f"voxel-{i}-{row}-{col}-{z}"]
                        close(
                            node["pos"],
                            offset(
                                foot,
                                dx * math.cos(yaw) - dy * math.sin(yaw),
                                dx * math.sin(yaw) + dy * math.cos(yaw),
                                (z + 0.5) * unit,
                            ),
                        )
                        close(node["size"], [unit - 0.6] * 3)
                        require(node["angle"] == -15, "Rotated projection geometry")
                    require(
                        sorted(round(n["pos"][2], 2) for n in vox)
                        == [36 + (j + 0.5) * unit for j in range(h)],
                        "Floating tower",
                    )
        for i, height in enumerate(b["screen"]):
            require(
                abs(by[f"shadow-col-{i}"]["size"][1] * st.cos - 66 * height) < 0.01,
                "Incorrect cast silhouette",
            )
    xy = [st.screen(n["pos"]) for n in tagged]
    require(
        all(SAFE[0] <= x <= SAFE[2] and SAFE[1] <= y <= SAFE[3] for x, y in xy),
        "Semantic anchor outside safe region",
    )
    # Measure a representative smallest distinguishing part in the actual submitted mesh,
    # projected onto a 360 px wide phone. Include tilt on the foreshortened axis.
    if f == "laser":
        feature = min(n["size"][1] for n in tagged if n["tag"].startswith("mirror-"))
        label = "mirror thickness"
    elif f == "maze":
        feature = min(n["size"][1] for n in tagged)
        label = "wall thickness"
    elif f == "gears":
        feature = min(
            max(math.hypot(*q) for q in n["outline"]) - min(math.hypot(*q) for q in n["outline"])
            for n in tagged
        )
        label = "tooth depth"
    elif f == "pipes":
        feature = min(2 * n["r"] for n in tagged)
        label = "pipe diameter"
    elif f == "search":
        feature = min(2 * n["r"] for n in tagged if "-spot-" in n["tag"])
        label = "eyespot diameter"
    elif f == "mismatch":
        feature = min(2 * n["r"] if n["kind"] == "tube" else n["size"][0] for n in tagged)
        label = "smallest control indicator"
    elif f == "fit":
        feature = math.hypot(*max(by["die"]["hole"], key=lambda q: math.hypot(*q))) - 85
        label = "lug depth"
    else:
        feature = min(n["size"][0] for n in tagged if n["tag"].startswith("voxel-"))
        label = "projected voxel edge"
    phone = round(feature * st.cos / 3, 2)
    require(phone >= 3, "Phone-scale distinguishing feature too small")
    return {
        "critical_feature": label,
        "feature_at_360px": phone,
        "checked_entities": len(tagged),
        "anchor_bounds": [
            round(min(x for x, y in xy)),
            round(min(y for x, y in xy)),
            round(max(x for x, y in xy)),
            round(max(y for x, y in xy)),
        ],
    }


def check_camera(st, receipt):
    tags = {n["tag"]: n for n in st.nodes if "tag" in n}
    require(set(tags) == set(receipt), "Missing rendered mesh")
    for k, n in tags.items():
        close(st.screen(n["pos"]), receipt[k], 0.1)
