#!/usr/bin/env python

import sys


def main():
    with open('day-03-input.txt') as f:
        values = f.readlines()
    wires = [x.strip().split(',')for x in values]
    moves = {'U': (0, 1), 'D': (0, -1), 'R': (1, 0), 'L': (-1, 0)}
    points = []
    for wire in wires:
        wire_points = {}
        point = (0, 0)
        distance = 1
        for step in wire:
            move_dir = step[:1]
            move_count = int(step[1:])
            for _ in range(move_count):
                point = (point[0] + moves[move_dir][0],
                         point[1] + moves[move_dir][1])
                if point not in wire_points:
                    wire_points[point] = distance
                distance += 1
        points.append(wire_points)

    intersections = set.intersection(*[set(x) for x in points])

    closest_by_distance = min(
        intersections, key=lambda x: abs(x[0]) + abs(x[1]))
    print(
        f'Part 1: {abs(closest_by_distance[0]) + abs(closest_by_distance[1])}')

    closest_by_steps = min(
        intersections, key=lambda x: points[0][x] + points[1][x])
    print(
        f'Part 2: {points[0][closest_by_steps] + points[1][closest_by_steps]}')


if __name__ == '__main__':
    main()
