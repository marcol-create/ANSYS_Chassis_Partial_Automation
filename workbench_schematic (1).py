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
#  Then imports material files into block A's Engineering Data:
#     any file in MATERIAL_DIR whose name contains "Al_HC" or "CF_Limits".
# =====================================================================

import os

# ---------------------------------------------------------------------
# CONFIG  --  edit these
# ---------------------------------------------------------------------
# Folder that holds the material data files (use a raw string on Windows).
MATERIAL_DIR = r"C:\Users\you\Desktop\materials"

# Import any file whose name CONTAINS one of these (case-insensitive).
MATERIAL_NAME_KEYS = ["Al_HC", "CF_Limits"]

# Only consider engineering-data file types. Broaden if your files differ.
MATERIAL_EXTS = (".xml", ".engd", ".eng")


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


def find_material_files(directory, key):
    """All files in directory whose name contains key and has a material ext."""
    hits = []
    for fname in os.listdir(directory):
        low = fname.lower()
        if key.lower() in low and low.endswith(MATERIAL_EXTS):
            hits.append(os.path.join(directory, fname).replace("\\", "/"))
    return hits


# ---------------------------------------------------------------------
# Block A : ACP (Pre)
# ---------------------------------------------------------------------
tmpl_acp = get_template("ACP (Pre)")
sysA = tmpl_acp.CreateSystem()
sysA.DisplayText = "Panels"
print("A created: Panels")

# --- Import material files into block A's Engineering Data ----------
eng = sysA.GetContainer(ComponentName="Engineering Data")
for key in MATERIAL_NAME_KEYS:
    files = find_material_files(MATERIAL_DIR, key)
    if not files:
        print("WARNING: no file matching '%s' (%s) in %s"
              % (key, "/".join(MATERIAL_EXTS), MATERIAL_DIR))
    for f in files:
        eng.Import(Source=f)
        print("Imported: %s" % f)

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
