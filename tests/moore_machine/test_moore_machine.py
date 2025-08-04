# type: ignore

import pytest

from state_machines.moore_machine import MooreMachine


def test_initial_state_not_in_states_dict():
  """Проверка, что отсутствие initial_state в states_dict вызывает KeyError."""
  invalid_dict: MooreMachine.Dict = {
    "S_0": ({0: "S_1", 1: "S_2"}, None),
    "S_1": ({0: "S_1", 1: "S_2"}, 1),
  }

  with pytest.raises(KeyError) as exc_info:
    MooreMachine(
      number="101",
      states_dict=invalid_dict,
      initial_state="S_3",  # отсутствует
      should_start=False,
    )

  assert "MooreMachine (in states_dict):" in str(exc_info.value)
  assert "Invalid initial state" in str(exc_info.value)
  assert "is not defined in states_dict" in str(exc_info.value)


def test_valid_states_dict():
  """Проверка, что валидный states_dict проходит без ошибок."""
  valid_dict: MooreMachine.Dict = {
    "S_0": ({0: "S_1", 1: "S_2"}, None),
    "S_1": ({0: "S_1", 1: "S_2"}, 1),
    "S_2": ({0: "S_1", 1: "S_2"}, 0),
  }

  machine = MooreMachine(
    number="101",
    states_dict=valid_dict,
    initial_state="S_0",
    should_start=False,
  )

  assert machine.GetAnswer() == ""


def test_invalid_state_name_type():
  """Проверка невалидного типа имени состояния."""
  invalid_dict: MooreMachine.Dict = {
    123: ({0: "S_1", 1: "S_2"}, 0),  # int - допустимо
    ("S_1",): ({0: "S_1", 1: "S_2"}, 1),  # кортеж - недопустимо
  }

  with pytest.raises(KeyError) as exc_info:
    MooreMachine(
      number="101",
      states_dict=invalid_dict,
      initial_state=123,
      should_start=False,
    )

  assert "Invalid state name" in str(exc_info.value)


def test_empty_transition_keys():
  """Проверка пустого словаря переходов."""
  invalid_dict: MooreMachine.Dict = {"S_0": ({}, None)}  # нет переходов

  with pytest.raises(KeyError) as exc_info:
    MooreMachine(
      number="101",
      states_dict=invalid_dict,
      initial_state="S_0",
      should_start=False,
    )

  assert "expected keys 0 and 1" in str(exc_info.value)


def test_extra_transition_keys():
  """Проверка лишних ключей в переходах."""
  invalid_dict: MooreMachine.Dict = {"S_0": ({0: "S_1", 1: "S_2", 2: "S_1"}, None)}

  with pytest.raises(KeyError) as exc_info:
    MooreMachine(
      number="101",
      states_dict=invalid_dict,
      initial_state="S_0",
      should_start=False,
    )

  assert "expected keys 0 and 1" in str(exc_info.value)


def test_missing_transition_keys():
  """Проверка отсутствия обязательных ключей."""
  test_cases: list[MooreMachine.Dict] = [
    {"S_0": ({1: "S_1"}, None)},  # нет 0
    {"S_0": ({0: "S_1"}, None)},  # нет 1
  ]

  for invalid_dict in test_cases:
    with pytest.raises(KeyError) as exc_info:
      MooreMachine(
        number="101",
        states_dict=invalid_dict,
        initial_state="S_0",
        should_start=False,
      )
    assert "expected keys 0 and 1" in str(exc_info.value)


def test_invalid_next_state_type():
  """Проверка невалидного типа следующего состояния."""
  invalid_dict: MooreMachine.Dict = {
    "S_0": ({0: None, 1: "S_1"}, None),  # None недопустим
    "S_1": ({0: 123.45, 1: "S_0"}, 1),  # float недопустим
  }

  with pytest.raises(ValueError) as exc_info:
    MooreMachine(
      number="101",
      states_dict=invalid_dict,
      initial_state="S_0",
      should_start=False,
    )

  assert "Invalid next_state name" in str(exc_info.value)


def test_invalid_output_digit():
  """Проверка невалидного выходного символа."""
  test_cases: list[MooreMachine.Dict] = [
    {"S_0": ({0: "S_1", 1: "S_2"}, 2)},  # 2 недопустимо
    {"S_0": ({0: "S_1", 1: "S_2"}, -1)},  # -1 недопустимо
    {"S_0": ({0: "S_1", 1: "S_2"}, "0")},  # строка недопустима
  ]

  for invalid_dict in test_cases:
    with pytest.raises(ValueError) as exc_info:
      MooreMachine(
        number="101",
        states_dict=invalid_dict,
        initial_state="S_0",
        should_start=False,
      )
    assert "expected 0, 1 or None" in str(exc_info.value)


def test_invalid_state_tuple_length():
  """Проверка неверной длины кортежа состояния."""
  invalid_dict: MooreMachine.Dict = {
    "S_0": ({0: "S_1", 1: "S_2"}, None, "extra"),  # лишний элемент
    "S_1": ({0: "S_1", 1: "S_2"},),  # недостаточно элементов
  }

  for states_dict in [invalid_dict]:
    with pytest.raises(ValueError) as exc_info:
      MooreMachine(
        number="101",
        states_dict=states_dict,
        initial_state="S_0",
        should_start=False,
      )
    assert "expected (dict, 0 or 1)" in str(exc_info.value)


def test_none_output_in_non_initial_state():
  """Проверка None в не-начальном состоянии."""
  valid_dict: MooreMachine.Dict = {
    "S_0": ({0: "S_1", 1: "S_2"}, None),  # None допустим в начальном
    "S_1": ({0: "S_1", 1: "S_2"}, None),  # None допустим в других состояниях
  }

  # Должно проходить без ошибок
  machine = MooreMachine(
    number="101",
    states_dict=valid_dict,
    initial_state="S_0",
    should_start=False,
  )
  assert machine.GetAnswer() == ""
