# =====================================================================
#  ACP (Pre) -- fabrics + "Full Panel" stackup   (compolyx API)
# =====================================================================
#  Runs INSIDE ACP:
#    - from Workbench:  setup.RunScript(ScriptPath="...this file...")
#    - or manually:     File > Run Script  in the ACP editor
#  Requires the materials to already be imported (Engineering Data).
#
#  Builds:
#    HC  fabric  = Aluminum Honeycomb, thickness 12.192
#    CF  fabric  = <imported CF material>, thickness 0.127
#    "Full Panel" stackup = CF/0, CF/90, HC/0, CF/0, CF/90
# =====================================================================

# ---- CONFIG: names must match the materials as they appear in ACP ----
MAT_HONEYCOMB = "Aluminum Honeycomb"
MAT_CF        = "CF"          # <-- set to the imported CF material's exact name
HC_THICKNESS  = 12.192        # in the model's length unit (mm if the model is mm-based)
CF_THICKNESS  = 0.127
STACKUP_NAME  = "Full Panel"

# ---- get the open ACP model ----
try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()

model = db.active_model
md    = model.material_data


def _require(collection, name, kind):
    try:
        return collection[name]
    except Exception:
        keys = ", ".join("'%s'" % k for k in collection.keys())
        raise KeyError("%s '%s' not found. Available: [%s]" % (kind, name, keys))


# ---- fabrics ----
hc = md.create_fabric(name="HC",
                      material=_require(md.materials, MAT_HONEYCOMB, "Material"),
                      thickness=HC_THICKNESS)
cf = md.create_fabric(name="CF",
                      material=_require(md.materials, MAT_CF, "Material"),
                      thickness=CF_THICKNESS)
print("Fabrics created: HC (%g), CF (%g)" % (hc.thickness, cf.thickness))

# ---- stackup: CF/0, CF/90, HC/0, CF/0, CF/90 ----
full = md.create_stackup(name=STACKUP_NAME)
for fab, ang in [(cf, 0.0), (cf, 90.0), (hc, 0.0), (cf, 0.0), (cf, 90.0)]:
    full.add_fabric(fab, ang)
print("Stackup '%s' created (%d fabrics)." % (STACKUP_NAME, len(full.fabrics)))

model.update()
print("Done.")
