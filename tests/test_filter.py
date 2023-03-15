from mmodel.filter import subnodes_by_inputs, subnodes_by_outputs


def test_subgraph_by_inputs(mmodel_G):
    """Test if the subgraph returns all nodes (including child nodes)."""

    subgraph_nodes = subnodes_by_inputs(mmodel_G, ["f"])
    assert set(subgraph_nodes) == {"poly", "multiply"}

    # multiple input parameters
    subgraph_nodes = subnodes_by_inputs(mmodel_G, ["f", "g"])
    assert set(subgraph_nodes) == {"poly", "multiply"}

    # whole graph
    subgraph_nodes = subnodes_by_inputs(mmodel_G, ["a"])
    assert set(subgraph_nodes) == {"add", "subtract", "poly", "multiply", "log"}


def test_subgraph_by_outputs(mmodel_G):
    """Test if the subgraph returns all nodes (including parent nodes)."""

    # return the original graph
    subgraph_nodes = subnodes_by_outputs(mmodel_G, ["k", "m"])
    assert set(subgraph_nodes) == {"add", "subtract", "poly", "multiply", "log"}

    subgraph_nodes = subnodes_by_outputs(mmodel_G, ["c", "k", "m"])
    assert set(subgraph_nodes) == {"add", "subtract", "poly", "multiply", "log"}

    # partial graph
    subgraph_nodes = subnodes_by_outputs(mmodel_G, ["m"])
    assert set(subgraph_nodes) == {"add", "log"}
