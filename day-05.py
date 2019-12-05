#!/usr/bin/env python

from collections import namedtuple

ADD = 1
MULTIPLY = 2
INPUT = 3
OUTPUT = 4
JUMP_IF_TRUE = 5
JUMP_IF_FALSE = 6
LESS_THAN = 7
EQUAL_TO = 8
HALT = 99

OPCODE_TO_INST_SIZE = {
    ADD: 4,
    MULTIPLY: 4,
    INPUT: 2,
    OUTPUT: 2,
    JUMP_IF_TRUE: 3,
    JUMP_IF_FALSE: 3,
    LESS_THAN: 4,
    EQUAL_TO: 4,
    HALT: 1
}

POSITION_MODE = 0
IMMEDIATE_MODE = 1


def main():
    with open('day-05-input.txt') as f:
        values = [int(x) for x in f.readline().strip().split(',')]

    memory = values[:]
    run_program(memory)


def run_program(memory):
    Parameter = namedtuple('Parameter', 'value mode')

    def resolve_parameter_value(parameter):
        return parameter.value if parameter.mode == IMMEDIATE_MODE else memory[parameter.value]

    i = 0
    while i < len(memory):
        mem_value = memory[i]
        opcode = mem_value % 100

        if opcode not in OPCODE_TO_INST_SIZE:
            raise ValueError(f'{opcode} is not a valid opcode')

        parameters = []
        param_mode = mem_value // 100
        for j in range(1, OPCODE_TO_INST_SIZE[opcode]):
            parameters.append(Parameter(memory[i + j], param_mode % 10))
            param_mode //= 10

        jumped = False

        if opcode == ADD:
            value1 = resolve_parameter_value(parameters[0])
            value2 = resolve_parameter_value(parameters[1])
            memory[parameters[2].value] = value1 + value2
        elif opcode == MULTIPLY:
            value1 = resolve_parameter_value(parameters[0])
            value2 = resolve_parameter_value(parameters[1])
            memory[parameters[2].value] = value1 * value2
        elif opcode == INPUT:
            memory[parameters[0].value] = int(input('Enter a value: '))
        elif opcode == OUTPUT:
            print(parameters[0].value if parameters[0].mode ==
                  IMMEDIATE_MODE else memory[parameters[0].value])
        elif opcode == JUMP_IF_TRUE:
            value = resolve_parameter_value(parameters[0])
            if value != 0:
                i = resolve_parameter_value(parameters[1])
                jumped = True
        elif opcode == JUMP_IF_FALSE:
            value = resolve_parameter_value(parameters[0])
            if value == 0:
                i = resolve_parameter_value(parameters[1])
                jumped = True
        elif opcode == LESS_THAN:
            value1 = resolve_parameter_value(parameters[0])
            value2 = resolve_parameter_value(parameters[1])
            memory[parameters[2].value] = 1 if value1 < value2 else 0
        elif opcode == EQUAL_TO:
            value1 = resolve_parameter_value(parameters[0])
            value2 = resolve_parameter_value(parameters[1])
            memory[parameters[2].value] = 1 if value1 == value2 else 0
        elif opcode == HALT:
            return

        if not jumped:
            i += OPCODE_TO_INST_SIZE[opcode]


if __name__ == '__main__':
    main()
