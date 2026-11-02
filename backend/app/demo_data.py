"""Fictional campus-scale network: schematic points, NOT verified accessible routes."""
from .routing import Edge, Network, Node

NODES = [
    Node("west", "West Gate", 9, 48),
    Node("library", "Library", 30, 46),
    Node("plaza", "Central Plaza", 51, 47),
    Node("engineering", "Engineering Hall", 73, 30),
    Node("science", "Science Center", 91, 47),
    Node("union", "Student Union", 29, 19),
    Node("garden", "Garden Path", 53, 17),
    Node("south", "South Entrance", 51, 81),
    Node("commons", "Dining Commons", 75, 74),
    Node("art", "Arts Building", 11, 78),
]

EDGES = [
    Edge("west-library", "west", "library", 160, 2),
    Edge("library-plaza", "library", "plaza", 145, 2),
    Edge("plaza-engineering", "plaza", "engineering", 155, 3),
    Edge("engineering-science", "engineering", "science", 170, 2),
    Edge("plaza-science", "plaza", "science", 210, 8),
    Edge("library-union", "library", "union", 150, 1),
    Edge("union-garden", "union", "garden", 145, 1),
    Edge("garden-engineering", "garden", "engineering", 165, 2),
    Edge("plaza-garden", "plaza", "garden", 95, 2, stairs=True),
    Edge("plaza-south", "plaza", "south", 170, 2),
    Edge("south-commons", "south", "commons", 160, 2),
    Edge("commons-science", "commons", "science", 175, 2),
    Edge("west-art", "west", "art", 160, 2),
    Edge("art-south", "art", "south", 190, 4, surface="gravel"),
    Edge("plaza-commons", "plaza", "commons", 195, 7),
    Edge("engineering-commons", "engineering", "commons", 230, 1),
]

NETWORK = Network(NODES, EDGES)
