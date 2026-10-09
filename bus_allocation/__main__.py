"""Runs two small example problems: python3 -m bus_allocation"""

from .allocator import assign


def main():
    L = 16
    roads = [(0, 1, 3), (0, 2, 5), (0, 3, 10), (1, 4, 1), (2, 5, 2), (5, 6, 3),
             (2, 7, 4), (0, 8, 1), (0, 9, 1), (0, 10, 1), (0, 11, 1), (6, 12, 2), (6, 13, 4),
             (6, 14, 3), (7, 15, 1)]

    students = [4, 10, 8, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 5, 7, 7,
                7, 7, 7, 15, 15, 7, 4, 8, 9]
    buses = [(0, 3, 5), (6, 5, 10), (15, 5, 10), (6, 5, 10)]
    print(assign(L, roads, students, buses, 5, 22))

    students = [5, 8, 3, 7, 7, 15, 15, 8, 15, 7, 6, 15]
    buses = [(0, 3, 5), (15, 5, 6)]
    print(assign(L, roads, students, buses, 5, 7))


if __name__ == "__main__":
    main()
