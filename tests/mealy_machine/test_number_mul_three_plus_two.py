import random

import pytest

from state_machines.mealy_machine import MealyMachine


# Общий словарь состояний автомата для умножения на 3 и сложения с 2
MUL_THREE_PLUS_TWO_STATES: MealyMachine.Dict = {
  "S_0": {
    0: ("S_1", 0),  # При входе 0: переходим в S_1, выход 0
    1: ("S_0", 1),  # При входе 1: остаёмся в S_0, выход 1
  },
  "S_1": {
    0: ("S_2", 1),  # При входе 0: переходим в S_2, выход 1
    1: ("S_5", 0),  # При входе 1: переходим в S_5, выход 0
  },
  "S_2": {
    0: ("S_2", 0),  # При входе 0: остаёмся в S_2, выход 0
    1: ("S_3", 1),  # При входе 1: переходим в S_3, выход 1
  },
  "S_3": {
    0: ("S_2", 1),  # При входе 0: переходим в S_2, выход 1
    1: ("S_4", 0),  # При входе 1: переходим в S_4, выход 0
  },
  "S_4": {
    0: ("S_3", 0),  # При входе 0: переходим в S_3, выход 0
    1: ("S_4", 1),  # При входе 1: остаёмся в S_4, выход 1
  },
  "S_5": {
    0: ("S_1", 0),  # При входе 0: переходим в S_1, выход 0
    1: ("S_6", 1),  # При входе 1: переходим в S_6, выход 1
  },
  "S_6": {
    0: ("S_3", 0),  # При входе 0: переходим в S_3, выход 0
    1: ("S_6", 1),  # При входе 1: остаёмся в S_6, выход 1
  },
}


@pytest.mark.parametrize(
  "number, expected",
  [
    (0, "10"),
    (1, "101"),
    (2, "1000"),
    (5, "10001"),
    (10, "100000"),
  ],
)
def test_mul_three_plus_two_small_numbers(number, expected):
  """Проверка умножения на 3 и сложения с 2 для малых чисел с выводом."""

  binary_input = bin(number)[2:]

  machine = MealyMachine(binary_input, MUL_THREE_PLUS_TWO_STATES, "S_0")

  assert machine.GetAnswer() == expected


def test_mul_three_plus_two_normal_numbers():
  """Проверка умножения на 3 и сложения с 2 для чисел от 0 до 9999."""

  for number in range(10000):
    binary_input = bin(number)[2:]
    expected = bin(number * 3 + 2)[2:]

    machine = MealyMachine(binary_input, MUL_THREE_PLUS_TWO_STATES, "S_0")

    assert machine.GetAnswer() == expected


def test_mul_three_plus_two_large_numbers():
  """Проверка умножения на 3 и сложения с 2 для больших чисел (случайная выборка)."""

  for _ in range(1000):  # Тестируем 1000 случайных чисел
    number = random.randint(0, 1000000)

    binary_input = bin(number)[2:]
    expected = bin(number * 3 + 2)[2:]

    machine = MealyMachine(binary_input, MUL_THREE_PLUS_TWO_STATES, "S_0")

    assert machine.GetAnswer() == expected


def test_mul_three_plus_two_with_leading_zeros():
  """Проверка обработки чисел с ведущими нулями."""

  machine = MealyMachine("00101", MUL_THREE_PLUS_TWO_STATES, "S_0")  # 5 в двоичном

  assert machine.GetAnswer() == "10001"  # 17 в двоичном
