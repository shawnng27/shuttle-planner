"""Tests for bus_allocation.assign: hand-written cases plus a brute-force comparison."""

import heapq
import itertools
import random

import pytest

from bus_allocation import assign


def shortest_distances(L, roads, source):
    adj = [[] for _ in range(L)]
    for u, v, w in roads:
        adj[u].append((v, w))
        adj[v].append((u, w))
    dist = [float("inf")] * L
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
    return dist


def is_valid(L, roads, students, buses, D, T, allocation):
    if len(allocation) != len(students):
        return False
    riders = [0] * len(buses)
    for student, bus in enumerate(allocation):
        if bus == -1:
            continue
        if shortest_distances(L, roads, buses[bus][0])[students[student]] > D:
            return False
        riders[bus] += 1
    return sum(riders) == T and all(lo <= n <= hi for n, (_, lo, hi) in zip(riders, buses))


def brute_force_feasible(L, roads, students, buses, D, T):
    options = []
    for location in students:
        reachable = [b for b, bus in enumerate(buses)
                     if shortest_distances(L, roads, bus[0])[location] <= D]
        options.append([-1] + reachable)
    return any(is_valid(L, roads, students, buses, D, T, list(combo))
               for combo in itertools.product(*options))


CITY_L = 16
CITY_ROADS = [(0, 1, 3), (0, 2, 5), (0, 3, 10), (1, 4, 1), (2, 5, 2), (5, 6, 3),
              (2, 7, 4), (0, 8, 1), (0, 9, 1), (0, 10, 1), (0, 11, 1), (6, 12, 2), (6, 13, 4),
              (6, 14, 3), (7, 15, 1)]


def test_feasible_example():
    students = [4, 10, 8, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 5, 7, 7,
                7, 7, 7, 15, 15, 7, 4, 8, 9]
    buses = [(0, 3, 5), (6, 5, 10), (15, 5, 10), (6, 5, 10)]
    allocation = assign(CITY_L, CITY_ROADS, students, buses, 5, 22)
    assert allocation is not None
    assert is_valid(CITY_L, CITY_ROADS, students, buses, 5, 22, allocation)


def test_infeasible_example():
    students = [5, 8, 3, 7, 7, 15, 15, 8, 15, 7, 6, 15]
    buses = [(0, 3, 5), (15, 5, 6)]
    assert assign(CITY_L, CITY_ROADS, students, buses, 5, 7) is None


def test_student_needed_by_farther_pickup():
    # Everyone is nearest to pickup 0, but bus 0 at pickup 2 needs one of them to reach its minimum.
    L, roads = 4, [(1, 2, 1), (2, 0, 1), (3, 0, 2)]
    students, buses = [3, 0, 0], [(2, 1, 4), (0, 1, 4)]
    allocation = assign(L, roads, students, buses, 3, 3)
    assert allocation is not None
    assert is_valid(L, roads, students, buses, 3, 3, allocation)


def test_more_buses_than_travellers():
    assert assign(2, [(0, 1, 1)], [0, 0, 1], [(0, 1, 2)] * 4, 5, 3) is None


def test_disconnected_city():
    L, roads = 1000, [(0, 1, 1)]
    allocation = assign(L, roads, [1, 1, 999], [(0, 1, 2)], 1, 2)
    assert allocation is not None and allocation[2] == -1


def random_case(rng):
    L = rng.randint(1, 6)
    roads, seen = [], set()
    for _ in range(rng.randint(0, L * (L - 1) // 2)):
        if L < 2:
            break
        u, v = rng.sample(range(L), 2)
        if (min(u, v), max(u, v)) not in seen:
            seen.add((min(u, v), max(u, v)))
            roads.append((u, v, rng.randint(1, 5)))
    students = [rng.randrange(L) for _ in range(rng.randint(1, 6))]
    buses = []
    for _ in range(rng.randint(1, 3)):
        lo = rng.randint(1, 3)
        buses.append((rng.randrange(L), lo, rng.randint(lo, 4)))
    return L, roads, students, buses, rng.randint(1, 6), rng.randint(1, len(students) + 1)


@pytest.mark.parametrize("seed", range(5))
def test_matches_brute_force(seed):
    rng = random.Random(seed)
    for _ in range(300):
        case = random_case(rng)
        allocation = assign(*case)
        if allocation is None:
            assert not brute_force_feasible(*case), case
        else:
            assert is_valid(*case, allocation), (case, allocation)
