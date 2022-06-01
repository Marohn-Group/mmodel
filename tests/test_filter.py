from tests.conftest import assert_graphs_equal
from mmodel.filter import subgraph_by_parameters, subgraph_by_nodes, subgraph_by_returns


def test_subgraph_by_parameters(mmodel_G):
    """Test if the subgraph returns all nodes (including children)"""

    subgraph1 = subgraph_by_parameters(mmodel_G, ["f"])
    subgraph2 = mmodel_G.subgraph(["multiply", "poly"])

    # have the same copy
    assert_graphs_equal(subgraph1, subgraph2)
    # retains oringinal graph
    assert subgraph1._graph == mmodel_G

    # multiple parameters
    subgraph3 = subgraph_by_parameters(mmodel_G, ["f", "g"])
    assert_graphs_equal(subgraph3, subgraph2)

    # whole graph
    subgraph4 = subgraph_by_parameters(mmodel_G, ["a"])
    assert_graphs_equal(subgraph4, mmodel_G)


def test_subgraph_by_nodes(mmodel_G):
    """Test if the subgraph contains all necessary nodes"""

    subgraph = subgraph_by_nodes(mmodel_G, ["subtract", "multiply"])

    assert sorted(list(subgraph.nodes)) == ["multiply", "subtract"]

def test_subgraph_by_returns(mmodel_G):
    """Test if the subgraph returns all nodes (including parents)"""

    # subgraph 1 and 2 should return the original graph
    subgraph1 = subgraph_by_returns(mmodel_G, ["k", "m"])
    assert_graphs_equal(subgraph1, mmodel_G)

    subgraph2 = subgraph_by_returns(mmodel_G, ["c", "k", "m"])
    assert_graphs_equal(subgraph2, mmodel_G)

    # partial graph
    subgraph3 = subgraph_by_returns(mmodel_G, ["m"])
    subgraph4 = mmodel_G.subgraph(["add", "log"])
    assert_graphs_equal(subgraph3, subgraph4)
