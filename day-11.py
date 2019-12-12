#!/usr/bin/env python

from collections import namedtuple
from itertools import permutations
from queue import Queue
from sys import exit, maxsize
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
ADJUST_REL_BASE = 9
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
    ADJUST_REL_BASE: 2,
    HALT: 1
}

POSITION_MODE = 0
IMMEDIATE_MODE = 1
RELATIVE_MODE = 2

DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3

Point = namedtuple('Point', 'x y')


class IntcodeComputer():
    def __init__(self, memory):
        self.__memory = {i: memory[i] for i in range(len(memory))}
        self.__inputs = Queue()
        self.__outputs = Queue()
        self.__is_halted = False
        self.__input_condition = Condition()
        self.__output_handler = None
        self.__last_output = 0
        self.__thread = Thread(target=self.__run_program, daemon=True)

    def __read_memory(self, address):
        return self.__memory[address] if address in self.__memory else 0

    def __write_memory(self, address, value):
        self.__memory[address] = value

    def __run_program(self):
        Parameter = namedtuple("Parameter", "value mode")

        def resolve_parameter_value(parameter):
            if parameter.mode == POSITION_MODE:
                return self.__read_memory(parameter.value)
            elif parameter.mode == IMMEDIATE_MODE:
                return parameter.value
            elif parameter.mode == RELATIVE_MODE:
                return self.__read_memory(relative_base + parameter.value)
            else:
                raise ValueError(
                    f"Unsupported parameter mode {parameter.mode}")

        def resolve_parameter_target_addr(parameter):
            if parameter.mode == POSITION_MODE:
                return parameter.value
            elif parameter.mode == RELATIVE_MODE:
                return relative_base + parameter.value
            else:
                raise ValueError(
                    f"Unsupported parameter mode {parameter.mode}")

        relative_base = 0
        i = 0
        while i < len(self.__memory):
            mem_value = self.__memory[i]
            opcode = mem_value % 100

            if opcode not in OPCODE_TO_INST_SIZE:
                raise ValueError(f"{opcode} is not a valid opcode")

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
                address = resolve_parameter_target_addr(parameters[2])
                self.__write_memory(address, value1 + value2)
            elif opcode == MULTIPLY:
                value1 = resolve_parameter_value(parameters[0])
                value2 = resolve_parameter_value(parameters[1])
                address = resolve_parameter_target_addr(parameters[2])
                self.__write_memory(address, value1 * value2)
            elif opcode == INPUT:
                address = resolve_parameter_target_addr(parameters[0])
                self.__write_memory(address, self.__get_next_input())
            elif opcode == OUTPUT:
                output = resolve_parameter_value(parameters[0])
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
                address = resolve_parameter_target_addr(parameters[2])
                self.__write_memory(address, 1 if value1 < value2 else 0)
            elif opcode == EQUAL_TO:
                value1 = resolve_parameter_value(parameters[0])
                value2 = resolve_parameter_value(parameters[1])
                address = resolve_parameter_target_addr(parameters[2])
                self.__write_memory(address, 1 if value1 == value2 else 0)
            elif opcode == ADJUST_REL_BASE:
                relative_base += resolve_parameter_value(parameters[0])
            elif opcode == HALT:
                break

            if not jumped:
                i += OPCODE_TO_INST_SIZE[opcode]

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

    def start_program(self):
        self.__thread.start()

    def wait_for_exit(self):
        while self.__thread.is_alive():
            self.__thread.join(0.1)


def main():
    with open("day-11-input.txt") as f:
        input_values = [int(x) for x in f.readline().strip().split(",")]

    computer = IntcodeComputer(input_values[:])
    white_panels = set()
    white_panels_all = set()
    robot_location = Point(0, 0)
    robot_direction = DIRECTION_UP
    is_output_for_color = True

    def handle_computer_output(output):
        nonlocal is_output_for_color
        nonlocal robot_location
        nonlocal robot_direction

        if is_output_for_color:
            if output == 0:
                if robot_location in white_panels:
                    white_panels.remove(robot_location)
            elif output == 1:
                white_panels.add(robot_location)
                white_panels_all.add(robot_location)
        else:
            if output == 0:
                robot_direction = (robot_direction - 1) % 4
            elif output == 1:
                robot_direction = (robot_direction + 1) % 4

            if robot_direction == DIRECTION_UP:
                robot_location = Point(robot_location.x, robot_location.y + 1)
            elif robot_direction == DIRECTION_RIGHT:
                robot_location = Point(robot_location.x + 1, robot_location.y)
            elif robot_direction == DIRECTION_DOWN:
                robot_location = Point(robot_location.x, robot_location.y - 1)
            elif robot_direction == DIRECTION_LEFT:
                robot_location = Point(robot_location.x - 1, robot_location.y)

            if robot_location in white_panels:
                computer.send_input(1)
            else:
                computer.send_input(0)

        is_output_for_color = not is_output_for_color

    computer.set_output_handler(handle_computer_output)
    computer.start_program()
    computer.send_input(0)
    computer.wait_for_exit()

    print(f"Part 1: {len(white_panels_all)}")

    computer = IntcodeComputer(input_values[:])
    white_panels = set([Point(0, 0)])
    robot_location = Point(0, 0)
    robot_direction = DIRECTION_UP
    is_output_for_color = True

    computer.set_output_handler(handle_computer_output)
    computer.start_program()
    computer.send_input(1)
    computer.wait_for_exit()

    print("Part 2:")
    print_points(list(white_panels))


def print_points(points):
    min_x = min([p.x for p in points])
    max_x = max([p.x for p in points])
    min_y = min([p.y for p in points])
    max_y = max([p.y for p in points])
    for y in reversed(range(max_y - min_y + 1)):
        for x in range(max_x - min_x + 1):
            if Point(x + min_x, y + min_y) in points:
                print('X', end='')
            else:
                print(' ', end='')
        print()


if __name__ == "__main__":
    main()
