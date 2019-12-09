#!/usr/bin/env python

from collections import namedtuple
from itertools import permutations
from queue import Queue
from sys import exit
from threading import Condition, Thread
from time import sleep

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


class IntcodeComputer():
    def __init__(self, memory):
        self.__memory = memory
        self.__inputs = Queue()
        self.__outputs = Queue()
        self.__is_halted = False
        self.__input_condition = Condition()
        self.__output_handler = None
        self.__last_output = 0
        self.__thread = Thread(target=self.__run_program)

    def __get_next_input(self):
        self.__input_condition.acquire()
        while self.__inputs.empty():
            self.__input_condition.wait()
        input = self.__inputs.get()
        self.__input_condition.release()
        return input

    def send_input(self, value):
        self.__input_condition.acquire()
        self.__inputs.put(value)
        self.__input_condition.notify()
        self.__input_condition.release()

    def get_last_output(self):
        return self.__last_output

    def set_output_handler(self, value):
        self.__output_handler = value

    def __run_program(self):
        Parameter = namedtuple('Parameter', 'value mode')

        def resolve_parameter_value(parameter):
            return parameter.value if parameter.mode == IMMEDIATE_MODE else self.__memory[parameter.value]

        outputs = []
        i = 0
        while i < len(self.__memory):
            mem_value = self.__memory[i]
            opcode = mem_value % 100

            if opcode not in OPCODE_TO_INST_SIZE:
                raise ValueError(f'{opcode} is not a valid opcode')

            parameters = []
            param_mode = mem_value // 100
            for j in range(1, OPCODE_TO_INST_SIZE[opcode]):
                parameters.append(
                    Parameter(self.__memory[i + j], param_mode % 10))
                param_mode //= 10

            jumped = False

            if opcode == ADD:
                value1 = resolve_parameter_value(parameters[0])
                value2 = resolve_parameter_value(parameters[1])
                self.__memory[parameters[2].value] = value1 + value2
            elif opcode == MULTIPLY:
                value1 = resolve_parameter_value(parameters[0])
                value2 = resolve_parameter_value(parameters[1])
                self.__memory[parameters[2].value] = value1 * value2
            elif opcode == INPUT:
                self.__memory[parameters[0].value] = self.__get_next_input()
            elif opcode == OUTPUT:
                output = (parameters[0].value if parameters[0].mode ==
                          IMMEDIATE_MODE else self.__memory[parameters[0].value])
                if self.__output_handler is not None:
                    self.__output_handler(output)
                self.__last_output = output
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
                self.__memory[parameters[2].value] = 1 if value1 < value2 else 0
            elif opcode == EQUAL_TO:
                value1 = resolve_parameter_value(parameters[0])
                value2 = resolve_parameter_value(parameters[1])
                self.__memory[parameters[2].value] = 1 if value1 == value2 else 0
            elif opcode == HALT:
                break

            if not jumped:
                i += OPCODE_TO_INST_SIZE[opcode]

        return outputs

    def start_program(self):
        self.__thread.start()

    def wait_for_exit(self):
        self.__thread.join()


def main():
    with open('day-07-input.txt') as f:
        input_values = [int(x) for x in f.readline().strip().split(',')]

    max_output = 0
    for values in permutations([0, 1, 2, 3, 4]):
        last_output = 0
        for i in range(5):
            amplifier = IntcodeComputer(input_values[:])
            amplifier.start_program()
            amplifier.send_input(values[i])
            amplifier.send_input(last_output)
            amplifier.wait_for_exit()
            last_output = amplifier.get_last_output()
        if last_output > max_output:
            max_output = last_output

    print(f'Part 1: {max_output}')

    max_output = 0
    for values in permutations([5, 6, 7, 8, 9]):
        last_output = 0
        amplifiers = [IntcodeComputer(input_values[:]) for i in range(5)]
        for i, amplifier in enumerate(amplifiers):
            amplifier.set_output_handler(
                lambda x, i=i: amplifiers[(i+1) % 5].send_input(x))
            amplifier.send_input(values[i])
            if i == 0:
                amplifier.send_input(0)
        for amplifier in amplifiers:
            amplifier.start_program()
        for amplifier in amplifiers:
            amplifier.wait_for_exit()
        last_output = amplifiers[4].get_last_output()
        if last_output > max_output:
            max_output = last_output

    print(f'Part 2: {max_output}')


if __name__ == '__main__':
    main()
