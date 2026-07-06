es = model.edge_sets["EdgeSet1"]
seat_sm.create_extension_guide(
    name="EdgeSet1_flush",
    edge_set=es,
    extrusion_guide_type="by_direction",
    direction=(1.0, 0.0, 0.0),
    radius=5.0, depth=1.0)
model.update()
