from app.demo_data import NETWORK
from app.routing import Edge, Network, Node


def test_stairs_avoidance():
    route = NETWORK.route("plaza", "garden", wheelchair=True)
    assert route is not None
    assert "plaza-garden" not in route.edge_ids
    assert len(route.node_ids) > 2


def test_direct_stairs_allowed_for_walking():
    route = NETWORK.route("plaza", "garden", wheelchair=False)
    assert route is not None
    assert route.edge_ids == ("plaza-garden",)


def test_steep_slope_avoided():
    route = NETWORK.route("plaza", "science", wheelchair=True)
    assert route is not None
    assert "plaza-science" not in route.edge_ids


def test_verified_blockage_simulation_changes_route():
    original = NETWORK.route("west", "library")
    alternative = NETWORK.route("west", "library", blocked_edges={"west-library"})
    assert original is not None and alternative is not None
    assert original.edge_ids == ("west-library",)
    assert "west-library" not in alternative.edge_ids


def test_same_start_destination():
    route = NETWORK.route("west", "west")
    assert route is not None
    assert route.distance_meters == 0
    assert route.edge_ids == ()


def test_unreachable():
    small = Network([Node("a", "A", 0, 0), Node("b", "B", 5, 0)], [])
    assert small.route("a", "b") is None


def test_invalid_edge_length():
    try:
        Network([Node("a", "A", 0, 0), Node("b", "B", 1, 0)], [Edge("e", "a", "b", -1)])
    except ValueError:
        pass
    else:
        assert False, "Negative lengths should fail"


def test_non_paved_avoidance():
    route = NETWORK.route("art", "south", avoid_unpaved=True)
    assert route is not None
    assert "art-south" not in route.edge_ids
