# =====================================================================
#  ACP DIAGNOSTIC -- inspect an OSS to see if its rosette is linked
# =====================================================================
#  Run in ACP via File > Run Script. Writes + opens acp_oss_diag.txt.
#  Send me the contents.
# =====================================================================
import os

try:
    db
except NameError:
    import compolyx
    db = compolyx.DB()
model = db.active_model

oss_keys = list(model.oriented_selection_sets.keys())
L = ["OSS count: %d" % len(oss_keys),
     "OSS names: %s" % ", ".join(oss_keys),
     "Rosettes in model: %s" % ", ".join(list(model.rosettes.keys())),
     ""]

if oss_keys:
    name = oss_keys[0]
    oss = model.oriented_selection_sets[name]
    L.append("Inspecting OSS: '%s'" % name)
    L.append("")
    L.append("ALL attributes:")
    L.append(", ".join([a for a in dir(oss) if not a.startswith("_")]))
    L.append("")
    for attr in ["rosettes", "rosette_selection_method", "element_sets",
                 "orientation_point", "orientation_direction",
                 "reference_direction", "reference_direction_field",
                 "orientation_direction_type", "draping"]:
        try:
            val = getattr(oss, attr)
            if isinstance(val, (list, tuple)):
                val = [getattr(v, "name", repr(v)) for v in val]
            L.append("%s = %s" % (attr, val))
        except Exception as ex:
            L.append("%s -> (none / %s)" % (attr, ex))

out = os.path.join(os.path.expanduser("~"), "acp_oss_diag.txt")
open(out, "w").write("\n".join(str(x) for x in L))
try:
    os.startfile(out)
except Exception:
    pass
print("wrote %s" % out)
