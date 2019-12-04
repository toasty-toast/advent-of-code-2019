#!/usr/bin/env python


def main():
    with open('day-04-input.txt') as f:
        bounds = f.readline().split('-')
        lower_bound = int(bounds[0])
        upper_bound = int(bounds[1])

    count1 = 0
    count2 = 0
    for i in range(lower_bound, upper_bound + 1):
        digits = get_digits(i)
        if is_increasing(digits):
            min_adjacent = min_adjacent_duplicates(digits)
            if min_adjacent >= 2:
                count1 += 1
            if min_adjacent == 2:
                count2 += 1

    print(f'Part 1: {count1}')
    print(f'Part 2: {count2}')


def get_digits(value):
    digits = []
    while value > 0:
        digits.insert(0, value % 10)
        value //= 10
    return digits


def min_adjacent_duplicates(digits):
    has_adjacent = False
    count = 0
    min = 100
    current = -1
    for i in range(len(digits)):
        if current != digits[i]:
            current = digits[i]
            if count >= 2 and count < min:
                min = count
            count = 1
        elif current == digits[i - 1]:
            has_adjacent = True
            count += 1
    if count >= 2 and count < min:
        min = count
    return min if has_adjacent else 0


def is_increasing(digits):
    for i in range(1, len(digits)):
        if digits[i] < digits[i - 1]:
            return False
    return True


if __name__ == '__main__':
    main()
