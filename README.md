# ANSYS Chassis (Semi) Automation Scripts

Python scripts that automate the repetitive parts of setting up composite and bumper analyses for the **Sunstruck** chassis in **ANSYS Workbench** and **ACP**.

---

# Included Scripts

| Script | Purpose |
|---------|---------|
| `workbench_setup(just_acp).py` | Creates an ACP-only Workbench project. Prompts for the chassis geometry, imports the material data from your computer, and completes the initial Mechanical setup (thickness + named selections). |
| `workbench_setup(bumpers_included).py` | Creates the full Workbench project with ACP, Front Bumper, and Side Bumper systems. Imports all geometry, meshes the bumper models, and creates the Static Structural and Structural Optimization analyses. |
| `workbench_setup(with_rollcage).py` | Same as the bumper workflow, with an additional Rollcage Mechanical Model that imports the rollcage geometry and generates a MultiZone hex mesh using the default Structural Steel material. |
| `acp_materials_rosettes.py` | Creates the Carbon Fiber and Honeycomb materials, the **Full Panel** layup, and one centered rosette for every element set (orientation is still manual). |
| `acp_oss_plies_solids.py` | Creates the Oriented Selection Sets (OSSs), Modeling Groups, plies, and solid models from the finalized rosettes. |

---

# Quick Workflow

Before opening ANSYS, prepare the CAD in Fusion by offsetting all chassis surfaces by **0.00 mm**, saving the bumper parts as separate STEP files, and exporting everything as `.step`.

If needed, download the material data files included in this repository.

1. **Run a Workbench setup script**
   - Open **Workbench → File → Scripting → Run Script File**.
   - Run one of:
     - `workbench_setup(just_acp).py`
     - `workbench_setup(bumpers_included).py`
     - `workbench_setup(with_rollcage).py`
   - The script imports the geometry, loads the material data, creates the named selections, and sets up the Mechanical models. The bumper and rollcage versions also generate their meshes and create the structural analyses.

2. **Generate the chassis mesh**
   - Open the ACP Mechanical model and generate the chassis mesh using the sizing appropriate for your analysis.

3. **Create the ACP model**
   - In **ACP → File → Run Script**, run `acp_materials_rosettes.py`.
   - The script creates the Carbon Fiber and Honeycomb materials, the **Full Panel** layup, and one centered rosette for every element set.

4. **Orient the rosettes**
   - Manually set the direction, flip, and offset direction for each rosette.

5. **Generate the remaining ACP objects**
   - Run `acp_oss_plies_solids.py`.
   - The script creates the OSSs, Modeling Groups, plies, and solid models, linking everything by matching names.
   - Assign draping where needed.

6. **Update ACP**
   - Update the ACP model, then return to Workbench to continue with the structural analyses.

---

# Manual Steps

The following steps are still completed manually:

- Mesh the chassis
- Orient the rosettes
- Assign draping

---

# 1. Workbench Setup

## Option A — ACP Only

### Required Geometry

- 📦 Chassis panels STEP file

In **ANSYS Workbench**:

```text
File → Scripting → Run Script File
```

Run:

```text
workbench_setup(just_acp).py
```

Select the chassis STEP file when prompted.

The script:

- Creates an ACP (Pre) system
- Imports the Carbon Fiber and Aluminum Honeycomb material data
- Imports the chassis geometry
- Opens ACP Mechanical
- Assigns a **1 mm** thickness to every surface body
- Creates a Named Selection for every body
- Saves the Workbench project

<img width="2560" height="1528" alt="image" src="https://github.com/user-attachments/assets/ecf6b3ed-9fdf-450a-bd1f-79e01b3e82bb" />

---

## Option B — ACP + Bumpers

### Required Geometry

- 📦 Chassis panels STEP file
- 🚗 Front bumper STEP file
- 🚗 Side bumper STEP file

Run:

```text
workbench_setup(bumpers_included).py
```

Select the chassis, front bumper, and side bumper STEP files when prompted.

The script creates:

### ACP

- ACP (Pre) system
- Imports Carbon Fiber and Aluminum Honeycomb material data
- Imports the chassis geometry
- Opens ACP Mechanical
- Assigns a **1 mm** thickness to every surface body
- Creates a Named Selection for every body

<img width="2560" height="1528" alt="image" src="https://github.com/user-attachments/assets/ecf6b3ed-9fdf-450a-bd1f-79e01b3e82bb" />

### Bumpers

- Front and Side Bumper Mechanical systems
- Imports the bumper geometry
- Assigns a **1 mm** thickness to all surface bodies
- Generates a **3 mm** mesh
- Creates Static Structural analyses
- Creates Structural Optimization analyses
- Saves the Workbench project

<img width="2560" height="1528" alt="image" src="https://github.com/user-attachments/assets/e8c1fed6-32fb-4de7-b3f2-82b00256fe39" />

<img width="2560" height="1600" alt="image" src="https://github.com/user-attachments/assets/b690991e-21c5-437b-bdd1-010254c5b993" />

---

## Option C — ACP + Bumpers + Rollcage

Same as Option B, with an additional Rollcage Mechanical Model.

### Required Geometry

- 📦 Chassis panels STEP file
- 🚗 Front bumper STEP file
- 🚗 Side bumper STEP file
- 🧰 Rollcage STEP file (solid hollow tubes)

Run:

```text
workbench_setup(with_rollcage).py
```

Select the geometry files in the following order:

1. Chassis
2. Front bumper
3. Side bumper
4. Rollcage

Everything from Option B, plus:

### Rollcage

- Imports the rollcage geometry
- Uses the default **Structural Steel** material
- Generates a MultiZone hex sweep mesh

> **Rollcage mesh note:** Set `ROLLCAGE_SIZE` (near the top of the script) to approximately **wall thickness ÷ 3**. This gives 2–3 elements through the tube wall while keeping the mesh efficient. Straight tube sections are swept into hex elements, with tetrahedra only used around joints. If a lighter model is preferred, the rollcage can instead be modeled using beam elements in SpaceClaim.

---

# 2. Mesh the Chassis

Open the ACP Mechanical model and generate the chassis mesh.

Choose the element size and any local refinement appropriate for your analysis.

<img width="2560" height="1540" alt="image" src="https://github.com/user-attachments/assets/cd505e9f-45f0-4a9a-a5b1-fe7f8f1bc9b8" />

---

# 3. Materials, Layup & Rosettes

In **ACP**:

```text
File → Run Script
```

Run:

```text
acp_materials_rosettes.py
```

The script creates:

- Carbon Fiber material
- Honeycomb material
- **Full Panel** layup

```text
Carbon Fiber (0°)
Carbon Fiber (90°)
Aluminum Honeycomb (0°)
Carbon Fiber (0°)
Carbon Fiber (90°)
```

- One centered rosette for every element set

<img height="460" alt="image" src="https://github.com/user-attachments/assets/13564262-c9be-40b3-acc7-a719828bf01a" />

---

# 4. Orient the Rosettes

Before continuing, orient each rosette manually.

Check the:

- Direction
- Flip
- Offset direction

Each panel may require a different orientation.

---

# 5. OSSs, Plies & Solid Models

In **ACP**:

```text
File → Run Script
```

Run:

```text
acp_oss_plies_solids.py
```

The script creates:

- One Oriented Selection Set (OSS) per element set
- One Modeling Group per element set
- One **Full Panel** ply per Modeling Group
- One Solid Model per element set
- **Analysis Ply Wise** extrusion
- Links all ACP objects by matching names

<img height="460" alt="image" src="https://github.com/user-attachments/assets/fccf9a34-4582-4a3e-9a8b-fa1b4c5328a8" />

<img height="460" alt="image" src="https://github.com/user-attachments/assets/4b692e55-4761-425c-a9fe-2e7063166209" />

### Final ACP Model

Update the ACP model, then return to Workbench to continue with the structural analyses.

---

# Notes

- Run each ACP script **once** on a clean ACP model.
- Generate the chassis mesh before running the ACP scripts.
- The bumper meshes are generated automatically by `workbench_setup(bumpers_included).py`.
- The rollcage mesh is generated automatically by `workbench_setup(with_rollcage).py`.
- Set `ROLLCAGE_SIZE` to approximately **wall thickness ÷ 3** for 2–3 elements through the tube wall.
- All ACP objects are linked by matching names, so avoid renaming element sets after the initial setup.
