def modifier_shortcut(model, modifier_dict):
    """Shortcut for quickly adding modifiers to the model."""

    G = model.graph  # copy of the graph
    for node, modifier_list in modifier_dict.items():
        modifiers = G.nodes[node]["modifiers"]
        modifiers = modifiers + modifier_list
        G.modify_node(node, modifiers=modifiers, inplace=True)

    return model.edit(graph=G)
