from collections.abc import Callable

import pytest

from state_machines.mealy_machine import MealyMachine
from state_machines.mealy_state import (
  MealyState,
)
from state_machines.mealy_step import MealyStepReason


# ---------- Вспомогательные функции для бинарных автоматов ----------


def make_condition(bit: str) -> Callable[[str], bool]:
  """Возвращает условие, которое истинно, если последний бит входной строки равен bit."""

  def condition(input_str: str) -> bool:
    return input_str[-1] == bit

  return condition


def make_output_adder(bit: str) -> Callable[[str], str]:
  """Возвращает функцию выхода, добавляющую bit в начало предыдущего выхода."""

  def add(prev_out: str) -> str:
    return bit + prev_out

  return add


def shift_processor(input_str: str) -> str:
  """Удаляет последний символ входной строки."""
  return input_str[:-1]


def build_transitions_from_dict(
  states_dict: dict,
) -> list[tuple[str, str, Callable, Callable, Callable]]:
  """
  Преобразует старый формат словаря состояний в список переходов для MealyMachine.
  Формат states_dict: {state_name: {0: (next_state, output), 1: (next_state, output)}}
  """

  transitions = []
  for src, trans in states_dict.items():
    for bit, (dst, out_bit) in trans.items():
      cond = make_condition(str(bit))
      func = make_output_adder(str(out_bit))
      transitions.append((src, dst, cond, func, shift_processor))

  return transitions


def make_binary_machine(
  states_dict: dict,
  initial_state: str,
  input_str: str,
  add_zeros: bool = True,
  zeros_amount: int = 4,
):
  """
  Создаёт MealyMachine для бинарных чисел.
  При add_zeros=True добавляет zeros_amount ведущих нулей к входной строке.
  """
  if add_zeros:
    input_str = input_str.zfill(len(input_str) + zeros_amount)
  transitions = build_transitions_from_dict(states_dict)

  return MealyMachine[str, str](
    transitions=transitions,
    initial_state=initial_state,
    initial_output="",
    initial_input=input_str,
    stop_condition=lambda input: len(input) == 0,
  )


# ---------- Тесты API и валидации ----------


class TestMealyMachineAPI:
  def test_add_duplicate_state(self):
    machine = MealyMachine[int, int]()
    machine.add_state(MealyState("A", {}))
    with pytest.raises(ValueError, match="State 'A' already exists"):
      machine.add_state(MealyState("A", {}))

  def test_remove_state(self):
    machine = MealyMachine[int, int]()
    machine.add_state(MealyState("A", {}))
    machine.remove_state("A")
    assert "A" not in machine.get_state_names()

  def test_remove_current_state_warns(self):
    machine = MealyMachine[int, int]()
    machine.add_state(MealyState("A", {}))
    machine.update_current_data("A", 0, 0)
    with pytest.warns(UserWarning, match="Removing current state 'A'"):
      machine.remove_state("A")
    assert machine.get_current_state_name() is None

  def test_update_states_with_duplicate(self):
    machine = MealyMachine[int, int]()
    with pytest.raises(ValueError, match="Duplicate state name in input: A"):
      machine.update_states(["A", "A"])

  def test_add_transition_duplicate_no_replace(self):
    machine = MealyMachine[int, int]()

    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    machine.add_transition("A", "B", cond, func, proc)
    with pytest.raises(ValueError, match="already exists"):
      machine.add_transition("A", "B", cond, func, proc, replace=False)

  def test_add_transition_replace(self):
    machine = MealyMachine[int, int]()

    def cond1(input):
      return True

    def cond2(input):
      return False

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    machine.add_transition("A", "B", cond1, func, proc)
    machine.add_transition("A", "B", cond2, func, proc, replace=True)
    # проверяем, что переход заменился
    transitions = machine.get_state_transitions("A")
    assert len(transitions) == 1
    assert transitions[0][1] is cond2

  def test_run_once_not_ready(self):
    machine = MealyMachine[int, int]()
    with pytest.raises(RuntimeError, match="Current state not set"):
      machine.run_once()

  def test_run_once_no_transition(self):
    machine = MealyMachine[int, int]()
    machine.add_state(MealyState("A", {}))
    machine.update_current_data("A", 0, 0)
    with pytest.warns(UserWarning, match="No transitions in state 'A'"):
      result = machine.run_once()
    assert result.reason == MealyStepReason.NO_TRANSITION

  def test_run_once_ambiguous(self):
    machine = MealyMachine[int, int]()

    def cond_true(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    machine.add_transition("A", "B", cond_true, func, proc)
    machine.add_transition("A", "C", cond_true, func, proc)
    machine.update_current_data("A", 0, 0)
    with pytest.raises(RuntimeError) as exc:
      machine.run_once()
    msg = str(exc.value)

    assert "Ambiguous transition: 2 transitions available" in msg
    assert "Current state: 'A'" in msg
    assert "to 'B' with:" in msg
    assert "to 'C' with:" in msg

  def test_run_once_exception_in_condition(self):
    machine = MealyMachine[str, str]()

    def bad_cond(input):
      raise RuntimeError("boom")

    machine.add_transition(
      "A", "B", bad_cond, lambda previous_output: previous_output, lambda input: input
    )
    machine.update_current_data("A", "", "0")
    with pytest.raises(RuntimeError, match="boom"):
      machine.run_once()

  def test_run_all_catches_exception(self):
    machine = MealyMachine[str, str]()

    def bad_cond(input):
      raise RuntimeError("boom")

    machine.add_transition(
      "A", "B", bad_cond, lambda previous_output: previous_output, lambda input: input
    )
    machine.update_current_data("A", "", "0")
    results = machine.run_all(raise_on_error=False)
    assert len(results) == 1
    assert results[0].reason == MealyStepReason.EXCEPTION
    assert isinstance(results[0].exception, RuntimeError)
    assert results[0].exception.args[0] == "boom"

  def test_run_all_stop_condition(self):

    machine = MealyMachine[str, str](stop_condition=lambda input: len(input) == 0)

    machine.add_state(MealyState("A", {}))
    machine.add_transition(
      "A",
      "B",
      condition=lambda input: True,
      function=lambda previous_output: previous_output,
      input_processor=lambda input: input,
    )
    machine.add_transition(
      "B",
      "A",
      condition=lambda input: True,
      function=lambda previous_output: previous_output,
      input_processor=lambda input: input,
    )
    machine.update_current_data("A", "", "0")

    result = machine.run_all()[-1]

    assert result.reason == MealyStepReason.STOP_CONDITION

  def test_results_methods(self):
    machine = MealyMachine[int, int]()

    def cond(input):
      return True

    def func(previous_output):
      return previous_output + 1

    def proc(input):
      return input + 1

    machine.add_transition("A", "A", cond, func, proc)
    machine.update_current_data("A", 0, 0)
    machine.run_once()
    results = machine.get_results()
    assert len(results) == 1
    data = machine.get_results_data()
    assert len(data) == 1
    assert data[0].output == 1
    tuples = machine.get_results_tuple()
    assert tuples[0] == (1, 1)
    outputs = machine.get_only_results()
    assert outputs[0] == 1
    final = machine.get_final_result()
    assert final == 1

  def test_clear_results(self):
    machine = MealyMachine[int, int]()

    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    machine.add_transition("A", "A", cond, func, proc)
    machine.update_current_data("A", 0, 0)
    machine.run_once()
    machine.clear_results()
    assert machine.get_results() == []


# ---------- Тесты бинарных операций ----------

# Словари состояний из старых тестов
MUL_THREE_STATES = {
  "S_0": {0: ("S_0", 0), 1: ("S_1", 1)},
  "S_1": {0: ("S_0", 1), 1: ("S_2", 0)},
  "S_2": {0: ("S_1", 0), 1: ("S_2", 1)},
}

MUL_THREE_PLUS_ONE_STATES = {
  "S_0": {0: ("S_1", 1), 1: ("S_4", 0)},
  "S_1": {0: ("S_1", 0), 1: ("S_2", 1)},
  "S_2": {0: ("S_1", 1), 1: ("S_3", 0)},
  "S_3": {0: ("S_2", 0), 1: ("S_3", 1)},
  "S_4": {0: ("S_5", 0), 1: ("S_6", 1)},
  "S_5": {0: ("S_1", 1), 1: ("S_4", 0)},
  "S_6": {0: ("S_2", 0), 1: ("S_6", 1)},
}

MUL_THREE_PLUS_TWO_STATES = {
  "S_0": {0: ("S_1", 0), 1: ("S_0", 1)},
  "S_1": {0: ("S_2", 1), 1: ("S_5", 0)},
  "S_2": {0: ("S_2", 0), 1: ("S_3", 1)},
  "S_3": {0: ("S_2", 1), 1: ("S_4", 0)},
  "S_4": {0: ("S_3", 0), 1: ("S_4", 1)},
  "S_5": {0: ("S_1", 0), 1: ("S_6", 1)},
  "S_6": {0: ("S_3", 0), 1: ("S_6", 1)},
}


def run_binary_test(
  states_dict, initial_state, number, expected, add_zeros=True, zeros_amount=4
):
  """Вспомогательная функция для тестирования бинарных автоматов."""
  input_str = bin(number)[2:]
  machine = make_binary_machine(
    states_dict, initial_state, input_str, add_zeros, zeros_amount
  )

  machine.run_all(raise_on_error=False)  # run_all останавливается по stop_condition
  result = machine.get_final_result()

  result = (result.lstrip("0") or "0") if result else "0"

  assert result == expected


class TestBinaryOperations:
  @pytest.mark.parametrize(
    "number,expected", [(0, "0"), (1, "11"), (2, "110"), (5, "1111"), (10, "11110")]
  )
  def test_mul_three_small(self, number, expected):
    run_binary_test(MUL_THREE_STATES, "S_0", number, expected)

  def test_mul_three_normal(self):
    for number in range(10000):
      expected = bin(number * 3)[2:]
      run_binary_test(
        MUL_THREE_STATES, "S_0", number, expected, add_zeros=True, zeros_amount=4
      )

  @pytest.mark.parametrize(
    "number,expected", [(0, "1"), (1, "100"), (2, "111"), (5, "10000"), (10, "11111")]
  )
  def test_mul_three_plus_one_small(self, number, expected):
    run_binary_test(MUL_THREE_PLUS_ONE_STATES, "S_0", number, expected)

  def test_mul_three_plus_one_normal(self):
    for number in range(10000):
      expected = bin(number * 3 + 1)[2:]
      run_binary_test(
        MUL_THREE_PLUS_ONE_STATES, "S_0", number, expected, add_zeros=True, zeros_amount=4
      )

  @pytest.mark.parametrize(
    "number,expected", [(0, "10"), (1, "101"), (2, "1000"), (5, "10001"), (10, "100000")]
  )
  def test_mul_three_plus_two_small(self, number, expected):
    run_binary_test(MUL_THREE_PLUS_TWO_STATES, "S_0", number, expected)

  def test_mul_three_plus_two_normal(self):
    for number in range(10000):
      expected = bin(number * 3 + 2)[2:]
      run_binary_test(
        MUL_THREE_PLUS_TWO_STATES, "S_0", number, expected, add_zeros=True, zeros_amount=4
      )

  def test_leading_zeros_mul_three(self):
    # Проверка, что добавление нулей меняет результат
    machine = make_binary_machine(
      MUL_THREE_STATES, "S_0", "101", add_zeros=True, zeros_amount=4
    )
    machine.run_all()

    result = machine.get_final_result()
    result_with_zeros = result.lstrip("0") if (result and result != "") else "0"

    machine = make_binary_machine(MUL_THREE_STATES, "S_0", "101", add_zeros=False)
    machine.run_all()

    result = machine.get_final_result()
    result_without_zeros = result.lstrip("0") if (result and result != "") else "0"

    assert result_with_zeros == "1111"
    assert result_without_zeros == "111"
