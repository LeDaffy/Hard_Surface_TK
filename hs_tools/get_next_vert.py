def get_next_vert(vert, selected, ordered):
    for e in vert.link_edges:
        for v in e.verts:
            if v in selected and v not in ordered:
                return v
