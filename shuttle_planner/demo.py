"""
Runs bus_allocation on a real OpenStreetMap walking network and saves an interactive map.

Usage (from the project root):
    .venv/bin/python -m shuttle_planner.demo
    .venv/bin/python -m shuttle_planner.demo --students 400 --walk 800 --seed 7
"""

import argparse
import random
import time

import folium
import networkx as nx

from bus_allocation import assign
from .osm_loader import CityMap

MONASH_MALAYSIA = (3.0640, 101.6008)
COLOURS = ["red", "blue", "green", "purple", "orange", "darkred", "cadetblue", "darkgreen",
           "pink", "darkblue", "beige", "darkpurple"]


def make_scenario(city, n_students, n_stops, buses_per_stop, walk, rng, clustered=0.7):
    """
    Places buses at real (or random) stops, and students so that a `clustered` fraction live
    within walking distance of some stop (as riders along a route would) and the rest anywhere.
    """
    stops = city.bus_stops(n_stops)
    while len(stops) < n_stops:
        stops.append(rng.randrange(city.L))

    graph = nx.Graph()
    graph.add_weighted_edges_from(city.roads)
    near_stop = [list(nx.single_source_dijkstra_path_length(graph, stop, cutoff=walk))
                 for stop in stops]

    students = []
    for _ in range(n_students):
        if rng.random() < clustered:
            students.append(rng.choice(rng.choice(near_stop)))
        else:
            students.append(rng.randrange(city.L))

    buses = []
    for stop in stops:
        for _ in range(buses_per_stop):
            minimum = rng.randint(5, 10)
            buses.append((stop, minimum, minimum + rng.randint(10, 20)))
    return students, buses


def draw_map(city, students, buses, allocation, walk, path):
    """Saves a folium map: pickups with a walking-radius circle, students coloured by bus."""
    # OpenStreetMap's own tile servers reject pages opened from disk (no Referer header), so use
    # CARTO's OSM-based basemap, which allows them
    fmap = folium.Map(location=city.center, zoom_start=15, tiles="CartoDB positron")

    for bus_id, (stop, minimum, maximum) in enumerate(buses):
        lat, lon = city.coords[stop]
        riders = allocation.count(bus_id) if allocation else 0
        folium.Circle((lat, lon), radius=walk, color=COLOURS[bus_id % len(COLOURS)],
                      fill=False, weight=1).add_to(fmap)
        folium.Marker((lat, lon), icon=folium.Icon(color=COLOURS[bus_id % len(COLOURS)], icon="bus", prefix="fa"),
                      tooltip=f"Bus {bus_id}: {riders} riders (min {minimum}, max {maximum})").add_to(fmap)

    for student_id, location in enumerate(students):
        bus_id = allocation[student_id] if allocation else -1
        colour = "#999999" if bus_id == -1 else COLOURS[bus_id % len(COLOURS)]
        label = "not travelling" if bus_id == -1 else f"bus {bus_id}"
        folium.CircleMarker(city.coords[location], radius=3, color=colour, fill=True,
                            fill_opacity=0.9, tooltip=f"Student {student_id}: {label}").add_to(fmap)

    fmap.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lat", type=float, default=MONASH_MALAYSIA[0])
    parser.add_argument("--lon", type=float, default=MONASH_MALAYSIA[1])
    parser.add_argument("--radius", type=int, default=1500, help="map radius in metres")
    parser.add_argument("--students", type=int, default=300)
    parser.add_argument("--stops", type=int, default=5)
    parser.add_argument("--buses-per-stop", type=int, default=2)
    parser.add_argument("--walk", type=int, default=600, help="max walking distance D in metres")
    parser.add_argument("--travellers", type=int, default=None, help="T; defaults to the midpoint of the bus capacities")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", default="shuttle_map.html")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    start = time.perf_counter()
    city = CityMap((args.lat, args.lon), args.radius)
    print(f"Loaded map: {city.L} locations, {len(city.roads)} roads ({time.perf_counter() - start:.1f}s)")

    students, buses = make_scenario(city, args.students, args.stops, args.buses_per_stop, args.walk, rng)
    T = args.travellers
    if T is None:
        T = (sum(b[1] for b in buses) + sum(b[2] for b in buses)) // 2
    print(f"Scenario: {len(students)} students, {len(buses)} buses, D = {args.walk} m, T = {T}")

    start = time.perf_counter()
    allocation = assign(city.L, city.roads, students, buses, args.walk, T)
    print(f"assign() took {time.perf_counter() - start:.2f}s")

    if allocation is None:
        print("No valid allocation. Try a larger --walk, fewer --travellers or more --students.")
    else:
        for bus_id, (stop, minimum, maximum) in enumerate(buses):
            print(f"  bus {bus_id:2} at location {stop:5}: {allocation.count(bus_id):3} riders (min {minimum}, max {maximum})")
        print(f"  travelling: {sum(1 for b in allocation if b != -1)} / {len(students)}")

    draw_map(city, students, buses, allocation, args.walk, args.out)
    print(f"Map saved to {args.out}")


if __name__ == "__main__":
    main()
