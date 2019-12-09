#!/usr/bin/env python

import sys

IMAGE_WIDTH = 25
IMAGE_HEIGHT = 6


def main():
    with open('day-08-input.txt') as f:
        input = [int(x) for x in f.readline()]

    layers = []
    for i in range(len(input) // (IMAGE_WIDTH * IMAGE_HEIGHT)):
        layers.append([input[j + (i * IMAGE_WIDTH * IMAGE_HEIGHT)]
                       for j in range(IMAGE_WIDTH * IMAGE_HEIGHT)])

    min_zeroes = sys.maxsize
    min_zeroes_layer = None
    for layer in layers:
        num_zeroes = sum(1 for i in layer if i == 0)
        if num_zeroes < min_zeroes:
            min_zeroes = num_zeroes
            min_zeroes_layer = layer

    num_ones = sum(1 for i in min_zeroes_layer if i == 1)
    num_twos = sum(1 for i in min_zeroes_layer if i == 2)
    print(f'Part 1: {num_ones * num_twos}')

    print(f'Part 2:')
    for i in range(IMAGE_HEIGHT):
        for j in range(IMAGE_WIDTH):
            layer_index = i * IMAGE_WIDTH + j
            for layer in layers:
                if layer[layer_index] == 2:
                    continue
                if layer[layer_index] == 0:
                    print(' ', end='')
                elif layer[layer_index] == 1:
                    print('X', end='')
                break
        print()


if __name__ == "__main__":
    main()
