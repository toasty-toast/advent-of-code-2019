#!/usr/bin/env python

import copy
import functools
import itertools
import math
import re


class Moon():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.start_x = x
        self.start_y = y
        self.start_z = z
        self.vx = 0
        self.vy = 0
        self.vz = 0

    def __str__(self):
        return f"x={self.x}, y={self.y}, z={self.z}, vx={self.vx}, vy={self.vy}, vz = {self.vz}"

    def total_energy(self):
        return (abs(self.x) + abs(self.y) + abs(self.z)) * (abs(self.vx) + abs(self.vy) + abs(self.vz))


def main():
    input_moons = []
    with open('day-12-input.txt') as f:
        re_matches = [re.match(r"^<x=(-?\d+), y=(-?\d+), z=(-?\d+)>$", x)
                      for x in f.readlines()]
        input_moons = [Moon(int(x.group(1)), int(x.group(2)), int(x.group(3)))
                       for x in re_matches]

    moons = [copy.deepcopy(x) for x in input_moons]
    for _ in range(1000):
        time_step(moons)
    print(f"Part 1: {sum([x.total_energy() for x in moons])}")

    moons = [copy.deepcopy(x) for x in input_moons]
    repeats = {}
    count = 1
    time_step(moons)
    while len(repeats) < 3:
        if 'x' not in repeats and all(m.x == m.start_x and m.vx == 0 for m in moons):
            repeats['x'] = count
        if 'y' not in repeats and all(m.y == m.start_y and m.vy == 0 for m in moons):
            repeats['y'] = count
        if 'z' not in repeats and all(m.z == m.start_z and m.vz == 0 for m in moons):
            repeats['z'] = count

        time_step(moons)
        count += 1

    print(f"Part 2: {lcm(list(repeats.values()))}")


def time_step(moons):
    for first, second in itertools.combinations(moons, 2):
        if first.x > second.x:
            first.vx -= 1
            second.vx += 1
        elif first.x < second.x:
            first.vx += 1
            second.vx -= 1
        if first.y > second.y:
            first.vy -= 1
            second.vy += 1
        elif first.y < second.y:
            first.vy += 1
            second.vy -= 1
        if first.z > second.z:
            first.vz -= 1
            second.vz += 1
        elif first.z < second.z:
            first.vz += 1
            second.vz -= 1
    for moon in moons:
        moon.x += moon.vx
        moon.y += moon.vy
        moon.z += moon.vz


def lcm(values):
    return functools.reduce(lambda a, b: (a * b) // math.gcd(a, b), values)


if __name__ == "__main__":
    main()
