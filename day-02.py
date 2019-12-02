#!/usr/bin/env python

import sys

PART_2_TARGET_VALUE = 19690720


def main():
    with open('day-02-input.txt') as f:
        values = f.readline().strip().split(',')
    values = [int(x) for x in values]

    memory = values[:]
    memory[1] = 12
    memory[2] = 2
    run_program(memory)
    print(f'Part 1: {memory[0]}')

    for noun in range(0, 100):
        for verb in range(0, 100):
            memory = values[:]
            memory[1] = noun
            memory[2] = verb
            run_program(memory)
            if memory[0] == PART_2_TARGET_VALUE:
                print(f'Part 2: {100 * noun + verb}')
                sys.exit(0)


def run_program(values):
    next_opcode = 0
    for i, opcode in enumerate(values):
        if i != next_opcode:
            continue

        if opcode == 1:
            input1_index = values[i + 1]
            input2_index = values[i + 2]
            target_index = values[i + 3]
            values[target_index] = values[input1_index] + values[input2_index]
            next_opcode = i + 4
        elif opcode == 2:
            input1_index = values[i + 1]
            input2_index = values[i + 2]
            target_index = values[i + 3]
            values[target_index] = values[input1_index] * values[input2_index]
            next_opcode = i + 4
        elif opcode == 99:
            return
        else:
            continue


if __name__ == '__main__':
    main()
