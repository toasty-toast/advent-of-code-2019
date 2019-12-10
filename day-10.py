#!/usr/bin/env python

from collections import namedtuple
import math

Asteroid = namedtuple('Asteroid', 'x y')


def main():
    with open("day-10-input.txt") as f:
        asteroids = [Asteroid(x, y) for y, line in enumerate(
            f.readlines()) for x, value in enumerate(line) if value == "#"]

    max_count = 0
    station = None
    for asteroid in asteroids:
        temp = asteroids[:]
        temp.remove(asteroid)
        count = len(set([math.atan2(target.y - asteroid.y,
                                    target.x - asteroid.x) for target in asteroids]))
        if count > max_count:
            max_count = count
            station = asteroid
    print(f"Part 1: {max_count}")

    asteroid_to_distance = {target: (
        (target.y - station.y)**2 + (target.x - station.x)**2)**(1/2) for target in asteroids}
    asteroid_to_angle = {target: -1 * math.atan2(
        target.y - station.y, target.x - station.x) for target in asteroids}
    angles = {angle: [] for angle in set(asteroid_to_angle.values())}
    for asteroid in asteroid_to_angle:
        angles[asteroid_to_angle[asteroid]].append(asteroid)
        angles[asteroid_to_angle[asteroid]].sort(
            key=lambda x: asteroid_to_distance[x])

    ordered_angles = sorted(angles.keys())
    for i, angle in enumerate(ordered_angles):
        if angle > math.pi / 2:
            ordered_angles = list(
                reversed(ordered_angles[:i])) + list(reversed(ordered_angles[i:]))
            break

    removed_count = 0
    i = 0
    while True:
        angle = ordered_angles[i]
        asteroids = angles[angle]
        if len(asteroids) > 0:
            removed = asteroids.pop(0)
            removed_count += 1
        if removed_count == 200:
            print(f"Part 2: {removed.x * 100 + removed.y}")
            break
        i = (i + 1) % len(ordered_angles)


if __name__ == "__main__":
    main()
