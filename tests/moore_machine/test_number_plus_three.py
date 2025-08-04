import random

import pytest

from state_machines.moore_machine import MooreMachine


# Общий словарь состояний для тестов
PLUS_THREE_STATES: MooreMachine.Dict = {
  "S_0": ({0: "S_1", 1: "S_2"}, None),
  "S_1": ({0: "S_3", 1: "S_4"}, 1),
  "S_2": ({0: "S_4", 1: "S_1"}, 0),
  "S_3": ({0: "S_5", 1: "S_3"}, 1),
  "S_4": ({0: "S_3", 1: "S_4"}, 0),
  "S_5": ({0: "S_5", 1: "S_3"}, 0),
}


@pytest.mark.parametrize(
  "number, expected",
  [
    (0, "11"),  # 0 + 3 = 3 (11)
    (1, "100"),  # 1 + 3 = 4 (100)
    (2, "101"),  # 2 + 3 = 5 (101)
    (5, "1000"),  # 5 + 3 = 8 (1000)
    (10, "1101"),  # 10 + 3 = 13 (1101)
  ],
)
def test_plus_three_small_numbers(number, expected):
  """Проверка прибавления 3 для малых чисел."""
  binary_input = bin(number)[2:]
  machine = MooreMachine(binary_input, PLUS_THREE_STATES, "S_0")
  assert machine.GetAnswer() == expected


def test_plus_three_normal_numbers():
  """Проверка чисел от 0 до 9999."""
  for number in range(10000):
    binary_input = bin(number)[2:]
    expected = bin(number + 3)[2:]
    machine = MooreMachine(binary_input, PLUS_THREE_STATES, "S_0")
    assert machine.GetAnswer() == expected


def test_plus_three_large_numbers_random():
  """Проверка больших чисел (случайная выборка)."""

  for _ in range(1000):  # Тестируем 1000 случайных чисел
    number = random.randint(0, 1000000)
    binary_input = bin(number)[2:]
    expected = bin(number + 3)[2:]
    machine = MooreMachine(binary_input, PLUS_THREE_STATES, "S_0")
    assert machine.GetAnswer() == expected


def test_plus_three_with_leading_zeros():
  """Проверка обработки чисел с ведущими нулями."""
  machine = MooreMachine("00101", PLUS_THREE_STATES, "S_0")  # 5 -> должно быть 8 (1000)
  assert machine.GetAnswer() == "1000"


def test_empty_input():
  """Проверка пустого ввода (должен обрабатываться как 0)."""
  machine = MooreMachine("", PLUS_THREE_STATES, "S_0")
  assert machine.GetAnswer() == "11"  # 0 + 3 = 3


def test_invalid_input():
  """Проверка некорректного ввода (недопустимые символы)."""
  with pytest.raises(ValueError):
    machine = MooreMachine("10201", PLUS_THREE_STATES, "S_0")  # '2' — недопустимый символ
    print(machine.GetAnswer())
