"""Accessibility-aware path selection on a small demonstrative graph.

Not intended for real-world navigation or safety-critical routing. Real accessibility
information must be reviewed, refreshed and verified before deployment.
"""
from __future__ import annotations

from dataclasses import dataclass
import heapq
import math
from typing import Iterable


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    x: float
    y: float


@dataclass(frozen=True)
class Edge:
    id: str
    source: str
    target: str
    meters: float
    slope_percent: float = 0.0
    stairs: bool = False
    surface: str = "paved"


@dataclass(frozen=True)
class Route:
    node_ids: tuple[str, ...]
    edge_ids: tuple[str, ...]
    distance_meters: float
    weighted_cost: float


class Network:
    def __init__(self, nodes: Iterable[Node], edges: Iterable[Edge]):
        self.nodes = {node.id: node for node in nodes}
        self.edges = {edge.id: edge for edge in edges}
        self.adjacency: dict[str, list[tuple[str, Edge]]] = {
            node_id: [] for node_id in self.nodes
        }
        if not self.nodes:
            raise ValueError("Network needs nodes")
        for edge in self.edges.values():
            if edge.source not in self.nodes or edge.target not in self.nodes:
                raise ValueError(f"Unknown endpoint in edge {edge.id}")
            if edge.meters <= 0:
                raise ValueError("Edge lengths must be positive")
            if edge.slope_percent < 0:
                raise ValueError("Store absolute slope magnitudes")
            self.adjacency[edge.source].append((edge.target, edge))
            self.adjacency[edge.target].append((edge.source, edge))

        # Use the smallest length-to-coordinate ratio, making the straight-line
        # estimate admissible even though demo coordinates aren't GPS units.
        self._heuristic_scale = min(
            (
                edge.meters
                / max(self._straight_line(edge.source, edge.target), 1e-9)
                for edge in self.edges.values()
            ),
            default=0.0,
        )

    def _straight_line(self, a: str, b: str) -> float:
        u, v = self.nodes[a], self.nodes[b]
        return math.hypot(u.x - v.x, u.y - v.y)

    def route(
        self,
        start: str,
        goal: str,
        *,
        wheelchair: bool = True,
        max_slope_percent: float = 6.0,
        avoid_unpaved: bool = False,
        blocked_edges: Iterable[str] = (),
    ) -> Route | None:
        if start not in self.nodes or goal not in self.nodes:
            raise ValueError("Unknown start or destination")
        if not (0 <= max_slope_percent <= 30):
            raise ValueError("Maximum slope must be between 0 and 30 percent")
        blocked = set(blocked_edges)
        if unknown := blocked - self.edges.keys():
            raise ValueError(f"Unknown edge IDs: {sorted(unknown)}")
        if start == goal:
            return Route((start,), (), 0.0, 0.0)

        # A* with an admissible heuristic. Weighted costs are >= edge distance.
        frontier: list[tuple[float, float, str]] = [
            (self._heuristic_scale * self._straight_line(start, goal), 0.0, start)
        ]
        best = {start: 0.0}
        previous: dict[str, tuple[str, str]] = {}

        while frontier:
            _, cost, current = heapq.heappop(frontier)
            if cost > best.get(current, float("inf")) + 1e-9:
                continue
            if current == goal:
                reversed_nodes = [goal]
                reversed_edges: list[str] = []
                cursor = goal
                while cursor != start:
                    predecessor, edge_id = previous[cursor]
                    reversed_edges.append(edge_id)
                    reversed_nodes.append(predecessor)
                    cursor = predecessor
                edge_ids = tuple(reversed(reversed_edges))
                return Route(
                    node_ids=tuple(reversed(reversed_nodes)),
                    edge_ids=edge_ids,
                    distance_meters=sum(self.edges[e].meters for e in edge_ids),
                    weighted_cost=cost,
                )

            for neighbor, edge in self.adjacency[current]:
                if edge.id in blocked:
                    continue
                if wheelchair and (edge.stairs or edge.slope_percent > max_slope_percent):
                    continue
                if avoid_unpaved and edge.surface != "paved":
                    continue
                # Prefer gentle paths even within the allowed maximum slope.
                slope_penalty = edge.slope_percent * 0.015 if wheelchair else 0.0
                new_cost = cost + edge.meters * (1.0 + slope_penalty)
                if new_cost + 1e-9 < best.get(neighbor, float("inf")):
                    best[neighbor] = new_cost
                    previous[neighbor] = (current, edge.id)
                    estimate = self._heuristic_scale * self._straight_line(neighbor, goal)
                    heapq.heappush(frontier, (new_cost + estimate, new_cost, neighbor))
        return None
