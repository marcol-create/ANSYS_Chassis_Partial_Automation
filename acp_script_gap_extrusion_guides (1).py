# =====================================================================
#  ACP (Pre) -- SCRIPT 3 : localized extrusion guides for flush gaps
# =====================================================================
#  Run INSIDE ACP (File > Run Script) AFTER Script 2 -- i.e. after the
#  rosettes, OSSs, modeling groups and solid models exist and have been
#  updated at least once.
#
#  PROBLEM
#    The seat wall sits at ~65 deg and extrudes NORMAL to its own face.
#    Two horizontal supports pass through the seat gaps (EdgeSet1..4).
#    Where the gap walls extrude along the tilted seat normal they only
#    kiss the horizontal support along one line -> a wedge void.
#
#  WHAT THIS DOES
#    Adds ONE extrusion guide per gap, scoped to that gap's edge set, that
#    re-points ONLY those edges toward horizontal (the flattened seat
#    normal). The seat body keeps extruding normal everywhere else.
#
#  THE FIX IN THIS VERSION
#    GUIDE_RADIUS is kept SMALL. The guide's radius is its sphere of
#    influence over the EXTRUSION (not the mesh). If it is large it reaches
#    past the gap into where the supports pass through and drags thin,
#    one-layer "tongues" of seat material along the supports. Keeping the
#    radius local to the gap edges removes those slivers. Your mesh
#    refinement lives in Mechanical (face sizings) and is unaffected by this.
# =====================================================================

# ---------------- CONFIG ----------------
SEAT_SET     = "Seat"          # element-set / solid-model name of the seat
SEAT_ROSETTE = "Seat"          # rosette whose normal == seat face normal
EDGE_SETS    = ["EdgeSet1", "EdgeSet2", "EdgeSet3", "EdgeSet4"]

UP_AXIS      = (0.0, 0.0, 1.0) # vertical axis; use (0,1,0) if Y is your up-axis
GUIDE_FLIP   = False           # negate the horizontal dir if the wedge gets WORSE

# Direction override. Leave None to derive from the flattened seat normal.
#   single vector : FIXED_HORIZONTAL = (1.0, 0.0, 0.0)
#   per-gap dict  : FIXED_HORIZONTAL = {"EdgeSet1": (..), "EdgeSet2": (..), ...}
FIXED_HORIZONTAL = None

# *** THE KNOB THAT KILLS THE SLIVERS ***
# Keep this small so the guide stays local to the gap edge and does NOT reach
# the supports. Rule of thumb: ~2-3x your gap element size. Your gap elements
# are 2.5 mm, so ~6 is the starting point. If tongues remain, refine the gap
# mesh finer (e.g. 1 mm) so you can use a smaller radius (~3) that resolves the
# transition without reaching the supports. If the wedge reopens, the seat
# cannot be both 65 deg and horizontal in one body -> split that strip out.
GUIDE_RADIUS = 6.0
GUIDE_DEPTH  = 1.0

# Per-gap overrides (keys are edge-set names) to fix ONE gap without touching others.
PER_GAP_FLIP   = {}   # e.g. {"EdgeSet3": True} -> negate just that gap's direction
PER_GAP_RADIUS = {}   # e.g. {"EdgeSet3": 0.5}  -> tighter radius for just that gap

DO_UPDATE        = True   # run model.update() at the end
REPLACE_EXISTING = True   # delete + recreate guides so re-runs (radius tuning) are clean

# ---------------- MODEL ----------------
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model

# ---------------- HELPERS ----------------
import math

def _unit(v):
    if v is None:
        return None
    m = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    return None if m < 1e-9 else (v[0] / m, v[1] / m, v[2] / m)

def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])

def get_item(collection, name):
    try:
        return collection[name]
    except Exception:
        return None

def rosette_normal(ros):
    """3rd axis (normal) of a rosette: a direct normal attr, else dir1 x dir2."""
    if ros is None:
        return None
    for a in ["normal", "dir3", "dir_3", "direction_3", "z_direction", "n"]:
        try:
            u = _unit(tuple(getattr(ros, a)))
            if u:
                return u
        except Exception:
            pass
    for a1, a2 in [("dir1", "dir2"), ("dir_1", "dir_2"),
                   ("direction_1", "direction_2"), ("x_direction", "y_direction")]:
        try:
            u = _unit(_cross(tuple(getattr(ros, a1)), tuple(getattr(ros, a2))))
            if u:
                return u
        except Exception:
            pass
    return None

def flatten_to_horizontal(v, up):
    """Remove the vertical (up) component so the vector lies in the ground plane."""
    up = _unit(up)
    if up is None or v is None:
        return None
    d = v[0] * up[0] + v[1] * up[1] + v[2] * up[2]
    return _unit((v[0] - d * up[0], v[1] - d * up[1], v[2] - d * up[2]))

def horizontal_for(esname):
    """Resolve the horizontal guide direction for one edge set -> (vec, source)."""
    if isinstance(FIXED_HORIZONTAL, dict):
        if esname in FIXED_HORIZONTAL:
            return _unit(tuple(FIXED_HORIZONTAL[esname])), "fixed(per-gap)"
    elif FIXED_HORIZONTAL is not None:
        return _unit(tuple(FIXED_HORIZONTAL)), "fixed"
    n_seat = rosette_normal(get_item(model.rosettes, SEAT_ROSETTE))
    if n_seat is None:
        return None, "no seat normal (rosette '%s' not found)" % SEAT_ROSETTE
    return flatten_to_horizontal(n_seat, UP_AXIS), "flattened seat normal"

def guide_exists(gname):
    try:
        return seat_sm.extrusion_guides[gname] is not None
    except Exception:
        return False

def delete_guide(gname):
    try:
        g = seat_sm.extrusion_guides[gname]
    except Exception:
        return True   # not there == nothing to delete
    for attempt in (lambda: g.delete(),
                    lambda: seat_sm.remove_extrusion_guide(g),
                    lambda: seat_sm.remove_extrusion_guide(gname)):
        try:
            attempt()
            return True
        except Exception:
            pass
    try:
        del seat_sm.extrusion_guides[gname]
        return True
    except Exception:
        return False

# ---------------- locate the seat solid model ----------------
seat_sm = get_item(model.solid_models, SEAT_SET)
if seat_sm is None:
    raise RuntimeError("Seat solid model '%s' not found. Available: [%s]"
                       % (SEAT_SET, ", ".join(model.solid_models.keys())))

# ---------------- one guide per gap ----------------
made, skipped, notes = 0, 0, []
for esname in EDGE_SETS:
    es = get_item(model.edge_sets, esname)
    if es is None:
        notes.append("%s: edge set NOT FOUND (have: [%s])"
                     % (esname, ", ".join(model.edge_sets.keys())))
        continue

    horiz, src = horizontal_for(esname)
    if horiz is None:
        notes.append("%s: no direction (%s) -- set FIXED_HORIZONTAL" % (esname, src))
        continue
    if GUIDE_FLIP or PER_GAP_FLIP.get(esname, False):
        horiz = (-horiz[0], -horiz[1], -horiz[2])

    radius = PER_GAP_RADIUS.get(esname, GUIDE_RADIUS)
    gname = "%s_flush" % esname

    if guide_exists(gname):
        if REPLACE_EXISTING:
            if not delete_guide(gname):
                notes.append("%s: exists and could NOT be deleted (remove it in the tree)" % gname)
                continue
        else:
            notes.append("%s: already exists (REPLACE_EXISTING off) -- skipped" % gname)
            skipped += 1
            continue

    try:
        seat_sm.create_extrusion_guide(name=gname, edge_set=es,
                                       direction=horiz,
                                       radius=radius, depth=GUIDE_DEPTH)
        made += 1
        notes.append("%s: OK r=%.3f dir=(%.3f,%.3f,%.3f) [%s]"
                     % (gname, radius, horiz[0], horiz[1], horiz[2], src))
    except Exception as ex:
        notes.append("%s: create FAILED: %s" % (esname, ex))

# ---------------- update ----------------
updated = False
if DO_UPDATE and made:
    try:
        model.update()
        updated = True
    except Exception as ex:
        notes.append("model.update() raised: %s" % ex)

# ---------------- always-visible summary (raised so it lands in a dialog) ----------------
summary = ("Guides created: %d   skipped: %d   updated: %s   (radius=%.3f)\n\n%s\n\n"
           "Section-cut check: wedge CLOSED + no tongues on the supports -> done.\n"
           "  tongues along a support   -> lower GUIDE_RADIUS (or PER_GAP_RADIUS).\n"
           "  wedge got WIDER on a gap  -> that gap needs GUIDE_FLIP / PER_GAP_FLIP.\n"
           "  wedge reopens when small  -> split that transition strip into its own set."
           % (made, skipped, updated, GUIDE_RADIUS, "\n".join(notes)))
raise RuntimeError(summary)
