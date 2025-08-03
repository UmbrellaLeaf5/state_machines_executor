import random

import pytest

from uniclasses.mealy_machine import MealyMachine


# Общий словарь состояний автомата для умножения на 3
MUL_THREE_STATES: MealyMachine.Dict = {
  "S_0": {0: ("S_0", 0), 1: ("S_1", 1)},
  "S_1": {0: ("S_0", 1), 1: ("S_2", 0)},
  "S_2": {0: ("S_1", 0), 1: ("S_2", 1)},
}


@pytest.mark.parametrize(
  "number, expected",
  [
    (0, "0"),  # 0 * 3 = 0
    (1, "11"),  # 1 * 3 = 3 (bin: 11)
    (2, "110"),  # 2 * 3 = 6 (bin: 110)
    (5, "1111"),  # 5 * 3 = 15 (bin: 1111)
    (10, "11110"),  # 10 * 3 = 30 (bin: 11110)
  ],
)
def test_mul_three_small_numbers(number, expected):
  """Проверка умножения на 3 для малых чисел с выводом."""

  binary_input = bin(number)[2:]

  machine = MealyMachine(binary_input, MUL_THREE_STATES, "S_0")

  assert machine.GetAnswer() == expected


def test_mul_three_normal_numbers():
  """Проверка умножения на 3 для чисел от 0 до 9999."""

  for number in range(10000):
    binary_input = bin(number)[2:]
    expected = bin(number * 3)[2:]

    machine = MealyMachine(binary_input, MUL_THREE_STATES, "S_0")

    assert machine.GetAnswer() == expected


def test_mul_three_large_numbers():
  """Проверка умножения на 3 для больших чисел (случайная выборка)."""

  for _ in range(1000):  # Тестируем 1000 случайных чисел
    number = random.randint(0, 1000000)

    binary_input = bin(number)[2:]
    expected = bin(number * 3)[2:]

    machine = MealyMachine(binary_input, MUL_THREE_STATES, "S_0")

    assert machine.GetAnswer() == expected


def test_mul_three_with_leading_zeros():
  """Проверка обработки чисел с ведущими нулями."""

  machine = MealyMachine("00101", MUL_THREE_STATES, "S_0")  # 5 в двоичном

  assert machine.GetAnswer() == "1111"  # 15 в двоичном
