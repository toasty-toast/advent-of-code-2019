#!/usr/bin/env python

import sys


def main():
    with open('day-01-input.txt') as f:
        values = f.readlines()
    values = [int(value.strip()) for value in values]

    total_without_recursion = sum([get_fuel(value, False) for value in values])
    print(f'Part 1: {total_without_recursion}')
    
    total_with_recursion = sum([get_fuel(value, True) for value in values])
    print(f'Part 2: {total_with_recursion}')


def get_fuel(value, recurse):
    fuel = max((value // 3) - 2, 0)
    if fuel == 0:
        return fuel
    return fuel if not recurse else fuel + get_fuel(fuel, recurse)


if __name__ == '__main__':
    main()
