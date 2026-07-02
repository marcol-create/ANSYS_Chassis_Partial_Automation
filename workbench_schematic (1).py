# =====================================================================
#  WORKBENCH PROJECT SCHEMATIC BUILDER  (IronPython)
# =====================================================================
#  Run from the Workbench Project window:
#     File > Scripting > Run Script File...  -> pick THIS file
#
#  Builds five systems, positioned and titled:
#     A  ACP (Pre)                "Panels"        (top-left)
#     B  Static Structural        "Side Impact"   (right of A)
#     C  Structural Optimization  "Front Impact"  (below B)
#     D  Mechanical Model         "Side bumper"   (below A)
#     E  Mechanical Model         "Front Bumper"  (below D)
#
#  Then searches your computer for material files whose names contain
#  "Al_HC" or "CF_Limits" and imports them into block A's Engineering Data.
# =====================================================================

import os

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
# Where to search (recursively). Default: your whole user profile, which
# covers Desktop, Documents, Downloads, OneDrive, etc. -- fast, and where
# user files almost always live.
SEARCH_ROOTS = [os.path.expanduser("~")]

# To search an ENTIRE DRIVE instead (slower, skips protected folders):
#   SEARCH_ROOTS = ["C:\\"]
# Or search several places:
#   SEARCH_ROOTS = [os.path.expanduser("~"), "D:\\", "E:\\projects"]

# Import files whose name CONTAINS one of these (case-insensitive).
MATERIAL_NAME_KEYS = ["Al_HC", "CF_Limits"]

# Only engineering-data file types. Broaden if your files differ.
MATERIAL_EXTS = (".xml", ".engd", ".eng")

# Folders to skip while walking (speeds things up, avoids junk/system dirs).
SKIP_DIRS = set(["appdata", "$recycle.bin", "windows", "program files",
                 "program files (x86)", "programdata", "node_modules",
                 ".git", "$windows.~ws", "system volume information"])


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------
def get_template(name, solver=None):
    """Resolve a template, tolerating either the Solver= form or the
    'Name (SOLVER)' form that some installs register instead."""
    try:
        if solver:
            return GetTemplate(TemplateName=name, Solver=solver)
        return GetTemplate(TemplateName=name)
    except Exception:
        if solver:
            return GetTemplate(TemplateName="%s (%s)" % (name, solver))
        raise


def find_material_files(roots, key):
    """Recursively find files under roots whose name contains key and has a
    material extension. Returns matches sorted newest-first."""
    hits = []
    seen = set()
    key_low = key.lower()
    for root in roots:
        if not os.path.isdir(root):
            print("WARNING: search root does not exist: %s" % root)
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # prune folders we don't want to descend into
            dirnames[:] = [d for d in dirnames if d.lower() not in SKIP_DIRS]
            for fname in filenames:
                low = fname.lower()
                if key_low in low and low.endswith(MATERIAL_EXTS):
                    full = os.path.join(dirpath, fname).replace("\\", "/")
                    if full not in seen:
                        seen.add(full)
                        hits.append(full)
    # newest file first (best guess at the current version)
    try:
        hits.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    except Exception:
        pass
    return hits


# ---------------------------------------------------------------------
# Block A : ACP (Pre)
# ---------------------------------------------------------------------
tmpl_acp = get_template("ACP (Pre)")
sysA = tmpl_acp.CreateSystem()
sysA.DisplayText = "Panels"
print("A created: Panels")

# --- Search the computer and import into block A's Engineering Data --
eng = sysA.GetContainer(ComponentName="Engineering Data")
print("Searching for material files under: %s" % ", ".join(SEARCH_ROOTS))
for key in MATERIAL_NAME_KEYS:
    files = find_material_files(SEARCH_ROOTS, key)
    if not files:
        print("WARNING: no file matching '%s' found." % key)
        continue
    chosen = files[0]
    eng.Import(Source=chosen)
    print("Imported ('%s'): %s" % (key, chosen))
    for extra in files[1:]:
        print("   (also found, NOT imported): %s" % extra)

# ---------------------------------------------------------------------
# Block B : Static Structural, right of A
# ---------------------------------------------------------------------
tmpl_struct = get_template("Static Structural", "ANSYS")
sysB = tmpl_struct.CreateSystem(Position="Right", RelativeTo=sysA)
sysB.DisplayText = "Side Impact"
print("B created: Side Impact")

# ---------------------------------------------------------------------
# Block C : Structural Optimization, below B
# ---------------------------------------------------------------------
tmpl_opt = get_template("Structural Optimization", "ANSYS")
sysC = tmpl_opt.CreateSystem(Position="Below", RelativeTo=sysB)
sysC.DisplayText = "Front Impact"
print("C created: Front Impact")

# ---------------------------------------------------------------------
# Block D : Mechanical Model, below A
# ---------------------------------------------------------------------
tmpl_mm = get_template("Mechanical Model")
sysD = tmpl_mm.CreateSystem(Position="Below", RelativeTo=sysA)
sysD.DisplayText = "Side bumper"
print("D created: Side bumper")

# ---------------------------------------------------------------------
# Block E : Mechanical Model, below D
# ---------------------------------------------------------------------
sysE = tmpl_mm.CreateSystem(Position="Below", RelativeTo=sysD)
sysE.DisplayText = "Front Bumper"
print("E created: Front Bumper")

print("Done.")

# --- Optional: save the project ------------------------------------
# Save(FilePath="C:/path/to/project.wbpj", Overwrite=True)
