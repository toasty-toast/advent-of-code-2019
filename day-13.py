#!/usr/bin/env python

from collections import namedtuple
from queue import Queue
from threading import Condition, Thread
from time import sleep

TILE_EMPTY = 0
TILE_WALL = 1
TILE_BLOCK = 2
TILE_PADDLE = 3
TILE_BALL = 4

Point = namedtuple('Point', 'x y')


class IntcodeComputer():
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

    def __init__(self, memory):
        self.__memory = {i: memory[i] for i in range(len(memory))}
        self.__inputs = Queue()
        self.__outputs = Queue()
        self.__is_halted = False
        self.__is_waiting_for_input = False
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
            if parameter.mode == IntcodeComputer.POSITION_MODE:
                return self.__read_memory(parameter.value)
            elif parameter.mode == IntcodeComputer.IMMEDIATE_MODE:
                return parameter.value
            elif parameter.mode == IntcodeComputer.RELATIVE_MODE:
                return self.__read_memory(relative_base + parameter.value)
            else:
                raise ValueError(
                    f"Unsupported parameter mode {parameter.mode}")

        def resolve_parameter_target_addr(parameter):
            if parameter.mode == IntcodeComputer.POSITION_MODE:
                return parameter.value
            elif parameter.mode == IntcodeComputer.RELATIVE_MODE:
                return relative_base + parameter.value
            else:
                raise ValueError(
                    f"Unsupported parameter mode {parameter.mode}")

        relative_base = 0
        i = 0
        while i < len(self.__memory):
            mem_value = self.__memory[i]
            opcode = mem_value % 100

            if opcode not in IntcodeComputer.OPCODE_TO_INST_SIZE:
                raise ValueError(f"{opcode} is not a valid opcode")

            parameters = []
            param_mode = mem_value // 100
            for j in range(1, IntcodeComputer.OPCODE_TO_INST_SIZE[opcode]):
                parameters.append(
                    Parameter(self.__memory[i + j], param_mode % 10))
                param_mode //= 10

            jumped = False

            if opcode == IntcodeComputer.ADD:
                value1 = resolve_parameter_value(parameters[0])
                value2 = resolve_parameter_value(parameters[1])
                address = resolve_parameter_target_addr(parameters[2])
                self.__write_memory(address, value1 + value2)
            elif opcode == IntcodeComputer.MULTIPLY:
                value1 = resolve_parameter_value(parameters[0])
                value2 = resolve_parameter_value(parameters[1])
                address = resolve_parameter_target_addr(parameters[2])
                self.__write_memory(address, value1 * value2)
            elif opcode == IntcodeComputer.INPUT:
                address = resolve_parameter_target_addr(parameters[0])
                self.__write_memory(address, self.__get_next_input())
            elif opcode == IntcodeComputer.OUTPUT:
                output = resolve_parameter_value(parameters[0])
                if self.__output_handler is not None:
                    self.__output_handler(output)
                self.__last_output = output
            elif opcode == IntcodeComputer.JUMP_IF_TRUE:
                value = resolve_parameter_value(parameters[0])
                if value != 0:
                    i = resolve_parameter_value(parameters[1])
                    jumped = True
            elif opcode == IntcodeComputer.JUMP_IF_FALSE:
                value = resolve_parameter_value(parameters[0])
                if value == 0:
                    i = resolve_parameter_value(parameters[1])
                    jumped = True
            elif opcode == IntcodeComputer.LESS_THAN:
                value1 = resolve_parameter_value(parameters[0])
                value2 = resolve_parameter_value(parameters[1])
                address = resolve_parameter_target_addr(parameters[2])
                self.__write_memory(address, 1 if value1 < value2 else 0)
            elif opcode == IntcodeComputer.EQUAL_TO:
                value1 = resolve_parameter_value(parameters[0])
                value2 = resolve_parameter_value(parameters[1])
                address = resolve_parameter_target_addr(parameters[2])
                self.__write_memory(address, 1 if value1 == value2 else 0)
            elif opcode == IntcodeComputer.ADJUST_REL_BASE:
                relative_base += resolve_parameter_value(parameters[0])
            elif opcode == IntcodeComputer.HALT:
                break

            if not jumped:
                i += IntcodeComputer.OPCODE_TO_INST_SIZE[opcode]

    def __get_next_input(self):
        self.__input_condition.acquire()
        while self.__inputs.empty():
            self.__is_waiting_for_input = True
            self.__input_condition.wait()
        self.__is_waiting_for_input = False
        input = self.__inputs.get()
        self.__input_condition.release()
        return input

    def waiting_for_input(self):
        return self.__is_waiting_for_input

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

    def has_exited(self):
        return not self.__thread.is_alive()

    def wait_for_exit(self):
        while self.__thread.is_alive():
            self.__thread.join(0.1)


def main():
    with open("day-13-input.txt") as f:
        input_values = [int(x) for x in f.readline().strip().split(",")]

    tiles = {}
    output_num, x, y, tile_id, score = 0, 0, 0, 0, 0
    ball_x, paddle_x = 0, 0
    def handle_computer_output(output):
        nonlocal output_num
        nonlocal x
        nonlocal y
        nonlocal tile_id
        nonlocal score
        nonlocal ball_x
        nonlocal paddle_x

        if output_num == 0:
            x = int(output)
        elif output_num == 1:
            y = int(output)
        else:
            if x == -1 and y == 0:
                score = int(output)
            else:
                tile_id = int(output)
                if tile_id == TILE_BALL:
                    ball_x = x
                elif tile_id == TILE_PADDLE:
                    paddle_x = x
                point = Point(x, y)
                tiles[point] = tile_id

        output_num = (output_num + 1) % 3

    computer = IntcodeComputer(input_values[:])
    computer.set_output_handler(handle_computer_output)
    computer.start_program()
    computer.wait_for_exit()

    block_count = sum(1 if tiles[p] == TILE_BLOCK else 0 for p in tiles.keys())
    print(f"Part 1: {block_count}")

    memory = input_values[:]
    memory[0] = 2
    computer = IntcodeComputer(memory)
    computer.set_output_handler(handle_computer_output)
    computer.start_program()

    while not computer.has_exited():
        if computer.waiting_for_input():
            if ball_x < paddle_x:
                computer.send_input(-1)
            elif ball_x > paddle_x:
                computer.send_input(1)
            else:
                computer.send_input(0)
        sleep(0.001)

    print(f"Part 2: {score}")


if __name__ == "__main__":
    main()
