#!/usr/bin/env python


def main():
    graph = {}
    with open('day-06-input.txt') as f:
        for line in f.readlines():
            target, source = line.strip().split(')')
            graph[source] = target

    print(f'Part 1: {get_checksum(graph)}')
    print(f'Part 2: {get_steps_to_santa(graph)}')


def get_checksum(graph):
    return sum([len(get_orbit_chain(graph, x)) - 1 for x in graph])


def get_orbit_chain(graph, start):
    value = start
    chain = [value]
    while value in graph:
        chain.append(graph[value])
        value = graph[value]
    return chain


def get_steps_to_santa(graph):
    you_chain = get_orbit_chain(graph, 'YOU')
    san_chain = get_orbit_chain(graph, 'SAN')
    for i, you_step in enumerate(you_chain):
        for j, san_step in enumerate(san_chain):
            if you_step == san_step:
                return i + j - 2


if __name__ == '__main__':
    main()
