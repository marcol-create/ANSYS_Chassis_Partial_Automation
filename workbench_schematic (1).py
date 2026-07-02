# =====================================================================
#  WORKBENCH PROJECT SCHEMATIC BUILDER  (IronPython)
# =====================================================================
#  Run from the Workbench Project window:
#     File > Scripting > Run Script File...  -> pick THIS file
#  (Make sure you pick this file, not an older copy in the same folder.)
#
#  Builds five systems, positioned and titled:
#     A  ACP (Pre)                "Panels"        (top-left)
#     B  Static Structural        "Side Impact"   (right of A)
#     C  Structural Optimization  "Front Impact"  (below B)
#     D  Mechanical Model         "Side bumper"   (below A)
#     E  Mechanical Model         "Front Bumper"  (below D)
# =====================================================================


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


# --- Block A : ACP (Pre) -------------------------------------------
tmpl_acp = get_template("ACP (Pre)")
sysA = tmpl_acp.CreateSystem()
sysA.DisplayText = "Panels"
print("A created: Panels")

# --- Block B : Static Structural, right of A -----------------------
tmpl_struct = get_template("Static Structural", "ANSYS")
sysB = tmpl_struct.CreateSystem(Position="Right", RelativeTo=sysA)
sysB.DisplayText = "Side Impact"
print("B created: Side Impact")

# --- Block C : Structural Optimization, below B --------------------
tmpl_opt = get_template("Structural Optimization", "ANSYS")
sysC = tmpl_opt.CreateSystem(Position="Below", RelativeTo=sysB)
sysC.DisplayText = "Front Impact"
print("C created: Front Impact")

# --- Block D : Mechanical Model, below A ---------------------------
tmpl_mm = get_template("Mechanical Model")
sysD = tmpl_mm.CreateSystem(Position="Below", RelativeTo=sysA)
sysD.DisplayText = "Side bumper"
print("D created: Side bumper")

# --- Block E : Mechanical Model, below D ---------------------------
sysE = tmpl_mm.CreateSystem(Position="Below", RelativeTo=sysD)
sysE.DisplayText = "Front Bumper"
print("E created: Front Bumper")

print("Done.")

# --- Optional: save the project ------------------------------------
# Save(FilePath="C:/path/to/project.wbpj", Overwrite=True)
