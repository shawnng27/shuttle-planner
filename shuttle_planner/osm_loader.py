"""Download a walking network from OpenStreetMap and convert it to bus_allocation's input format."""

import osmnx as ox


class CityMap:
    """
    A real road network with locations relabelled 0..L-1.

    Attributes:
        - graph: the undirected osmnx graph (keeps coordinates for plotting)
        - L: number of locations
        - roads: list of (u, v, length_in_metres), at most one road per pair of locations
        - node_ids: node_ids[i] is the OSM node ID of location i
        - coords: coords[i] is the (lat, lon) of location i
    """

    def __init__(self, center, radius):
        """
        Downloads the walking network within radius metres of center = (lat, lon).
        """
        self.center = center
        self.radius = radius
        self.graph = ox.convert.to_undirected(
            ox.graph_from_point(center, dist=radius, network_type="walk")
        )

        self.node_ids = list(self.graph.nodes)
        self.L = len(self.node_ids)
        self._index = {osm_id: i for i, osm_id in enumerate(self.node_ids)}
        self.coords = [(self.graph.nodes[n]["y"], self.graph.nodes[n]["x"]) for n in self.node_ids]
        self.roads = self._build_roads()

    def _build_roads(self):
        """
        Keeps the shortest road between each pair of locations, since bus_allocation
        allows only one road per pair. Lengths are rounded up to whole metres (minimum 1).
        """
        shortest = {}
        for u, v, data in self.graph.edges(data=True):
            if u == v:
                continue
            a, b = self._index[u], self._index[v]
            key = (min(a, b), max(a, b))
            length = max(1, round(data["length"]))
            if key not in shortest or length < shortest[key]:
                shortest[key] = length
        return [(a, b, w) for (a, b), w in shortest.items()]

    def nearest_location(self, lat, lon):
        """Returns the location ID of the intersection nearest to (lat, lon)."""
        return self._index[ox.distance.nearest_nodes(self.graph, X=lon, Y=lat)]

    def bus_stops(self, limit):
        """
        Returns up to limit location IDs of real bus stops from OSM, snapped to the
        nearest intersection, with duplicates removed.
        """
        try:
            stops = ox.features_from_point(self.center, {"highway": "bus_stop"}, dist=self.radius)
        except ox._errors.InsufficientResponseError:
            return []

        locations = []
        for geometry in stops.geometry:
            point = geometry.centroid
            location = self.nearest_location(point.y, point.x)
            if location not in locations:
                locations.append(location)
            if len(locations) == limit:
                break
        return locations
