# type: ignore

import pytest

from uniclasses.mealy_machine import MealyMachine


def test_initial_state_not_in_states_dict():
  """Проверка, что отсутствие initial_state в states_dict вызывает KeyError."""

  valid_dict: MealyMachine.Dict = {
    "S_0": {0: ("S_0", 0), 1: ("S_1", 1)},
    "S_1": {0: ("S_0", 1), 1: ("S_2", 0)},
  }

  with pytest.raises(KeyError) as exc_info:
    MealyMachine(
      number="101",
      states_dict=valid_dict,
      initial_state="S_3",  # отсутствует в states_dict
      should_start=False,
    )

  assert "MealyMachine (in states_dict):" in str(exc_info.value)
  assert "Invalid initial state" in str(exc_info.value)
  assert "is not defined in states_dict" in str(exc_info.value)
  assert "Available states:" in str(exc_info.value)


def test_valid_states_dict():
  """Проверка, что валидный states_dict проходит без ошибок."""

  valid_dict: MealyMachine.Dict = {
    "S_0": {0: ("S_0", 0), 1: ("S_1", 1)},
    "S_1": {0: ("S_0", 1), 1: ("S_2", 0)},
    "S_2": {0: ("S_1", 0), 1: ("S_2", 1)},
  }

  machine = MealyMachine(
    number="101",
    states_dict=valid_dict,
    initial_state="S_0",
    should_start=False,
  )

  assert machine.GetAnswer() == ""


def test_invalid_state_name_type():
  """Проверка, что невалидное имя состояния вызывает исключение."""

  invalid_dict: MealyMachine.Dict = {
    123: {0: ("S_0", 0), 1: ("S_1", 1)},  # int - допустимо
    ("S_1",): {0: ("S_0", 1), 1: ("S_2", 0)},  # кортеж - недопустимо
  }

  with pytest.raises(KeyError) as exc_info:
    MealyMachine(
      number="101",
      states_dict=invalid_dict,
      initial_state=123,
      should_start=False,
    )

  assert "MealyMachine (in states_dict):" in str(exc_info.value)
  assert "Invalid state name" in str(exc_info.value)
  assert "expected str or int, got" in str(exc_info.value)


def test_invalid_transition_keys():
  """Проверка, что отсутствие ключей 0 и 1 вызывает исключение."""

  invalid_dicts: list[MealyMachine.Dict] = [
    {"S_0": {}},  # нет ключей
    {"S_0": {0: ("S_0", 0)}},  # нет ключа 1
    {"S_0": {1: ("S_1", 1)}},  # нет ключа 0
    {"S_0": {0: ("S_0", 0), 1: ("S_1", 1), 2: ("S_2", 0)}},  # лишний ключ
  ]

  for invalid_dict in invalid_dicts:
    with pytest.raises(KeyError) as exc_info:
      MealyMachine(
        number="101",
        states_dict=invalid_dict,
        initial_state="S_0",
        should_start=False,
      )

    assert "MealyMachine (in states_dict):" in str(exc_info.value)
    assert "Invalid transitions in state" in str(exc_info.value)
    assert "expected keys {0, 1}, but got" in str(exc_info.value)


def test_invalid_next_state_type():
  """Проверка, что невалидный тип next_state вызывает исключение."""

  invalid_dict: MealyMachine.Dict = {
    "S_0": {0: ("S_0", 0), 1: (123, 1)},  # int - допустимо
    "S_1": {0: ("S_0", 1), 1: (None, 0)},  # None - недопустимо
  }

  with pytest.raises(ValueError) as exc_info:
    MealyMachine(
      number="101",
      states_dict=invalid_dict,
      initial_state="S_0",
      should_start=False,
    )

  assert "MealyMachine (in states_dict):" in str(exc_info.value)
  assert "Invalid next state in transition" in str(exc_info.value)
  assert "->" in str(exc_info.value)
  assert "expected str or int, got" in str(exc_info.value)


def test_invalid_output_digit():
  """Проверка, что невалидный output_digit вызывает исключение."""

  invalid_dicts: list[MealyMachine.Dict] = [
    {"S_0": {0: ("S_0", 2), 1: ("S_1", 1)}},  # 2 - недопустимо
    {"S_0": {0: ("S_0", 0), 1: ("S_1", -1)}},  # -1 - недопустимо
    {"S_0": {0: ("S_0", "0"), 1: ("S_1", 1)}},  # строка - недопустимо
  ]

  for invalid_dict in invalid_dicts:
    with pytest.raises(ValueError) as exc_info:
      MealyMachine(
        number="101",
        states_dict=invalid_dict,
        initial_state="S_0",
        should_start=False,
      )

    assert "MealyMachine (in states_dict):" in str(exc_info.value)
    assert "Invalid output digit in transition" in str(exc_info.value)
    assert "expected 0 or 1, got" in str(exc_info.value)
