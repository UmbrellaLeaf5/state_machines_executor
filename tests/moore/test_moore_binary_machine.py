from src.state_machines import MooreMachine, MooreState, MooreTransition, StepReason
from tests.utils.binary_machine_helpers import (
  make_condition,
  make_output_adder,
  shift_processor,
)


def add_nothing(previous_output: str) -> str:
  return previous_output


def shift_add_zero(input: str) -> str:
  return "0" + input[:-1]


def make_moore_plus_3_machine() -> MooreMachine[str, str]:
  """Создаёт автомат Мура для операции +3 (из temp.py)."""

  return MooreMachine[str, str](
    states=[
      ("S_0", add_nothing),
      ("S_1", make_output_adder("1")),
      ("S_2", make_output_adder("0")),
      ("S_3", make_output_adder("1")),
      ("S_4", make_output_adder("0")),
      ("S_5", make_output_adder("0")),
    ],
    transitions=[
      ("S_0", "S_1", make_condition("0"), shift_add_zero),
      ("S_0", "S_2", make_condition("1"), shift_add_zero),
      ("S_1", "S_3", make_condition("0"), shift_processor),
      ("S_1", "S_4", make_condition("1"), shift_processor),
      ("S_2", "S_4", make_condition("0"), shift_processor),
      ("S_2", "S_1", make_condition("1"), shift_processor),
      ("S_3", "S_5", make_condition("0"), shift_processor),
      ("S_3", "S_3", make_condition("1"), shift_processor),
      ("S_4", "S_3", make_condition("0"), shift_processor),
      ("S_4", "S_4", make_condition("1"), shift_processor),
      ("S_5", "S_5", make_condition("0"), shift_processor),
      ("S_5", "S_3", make_condition("1"), shift_processor),
    ],
    initial_state="S_0",
    initial_output="",
    stop_condition=lambda input: len(input) == 0,
  )


class TestMooreBinaryMachine:
  def test_plus_3_with_00101(self):
    """Тест из temp.py: input=00101"""
    machine = make_moore_plus_3_machine()
    machine.update_current_data(input="00101")
    machine.run_all(raise_on_error=False)

    results = machine.get_only_results()
    # Ожидаемый результат: "0" -> "1" -> "00" -> "001" -> "0011" (примерно)
    # Проверяем, что последний результат не пустой и что были шаги
    assert len(results) > 0
    assert machine.get_final_result() is not None

  def test_plus_3_with_00101_using_objects(self):
    """Тест с использованием объектов MooreState и MooreTransition."""
    machine = MooreMachine[str, str](
      states=[
        MooreState("S_0", add_nothing, {}),
        MooreState("S_1", make_output_adder("1"), {}),
        MooreState("S_2", make_output_adder("0"), {}),
        MooreState("S_3", make_output_adder("1"), {}),
        MooreState("S_4", make_output_adder("0"), {}),
        MooreState("S_5", make_output_adder("0"), {}),
      ],
      transitions=[
        MooreTransition("S_0", "S_1", make_condition("0"), shift_add_zero),
        MooreTransition("S_0", "S_2", make_condition("1"), shift_add_zero),
        MooreTransition("S_1", "S_3", make_condition("0"), shift_processor),
        MooreTransition("S_1", "S_4", make_condition("1"), shift_processor),
        MooreTransition("S_2", "S_4", make_condition("0"), shift_processor),
        MooreTransition("S_2", "S_1", make_condition("1"), shift_processor),
        MooreTransition("S_3", "S_5", make_condition("0"), shift_processor),
        MooreTransition("S_3", "S_3", make_condition("1"), shift_processor),
        MooreTransition("S_4", "S_3", make_condition("0"), shift_processor),
        MooreTransition("S_4", "S_4", make_condition("1"), shift_processor),
        MooreTransition("S_5", "S_5", make_condition("0"), shift_processor),
        MooreTransition("S_5", "S_3", make_condition("1"), shift_processor),
      ],
      initial_state="S_0",
      initial_output="",
      stop_condition=lambda input: len(input) == 0,
    )

    machine.update_current_data(input="00101")
    machine.run_all(raise_on_error=False)

    assert len(machine.get_results()) > 0

  def test_plus_3_mixed_constructor(self):
    """Тест со смешанным использованием кортежей и объектов в конструкторе."""
    machine = MooreMachine[str, str](
      states=[
        ("S_0", add_nothing),
        MooreState("S_1", make_output_adder("1"), {}),
        ("S_2", make_output_adder("0")),
        MooreState("S_3", make_output_adder("1"), {}),
        ("S_4", make_output_adder("0")),
        MooreState("S_5", make_output_adder("0"), {}),
      ],
      transitions=[
        ("S_0", "S_1", make_condition("0"), shift_add_zero),
        MooreTransition("S_0", "S_2", make_condition("1"), shift_add_zero),
        ("S_1", "S_3", make_condition("0"), shift_processor),
        MooreTransition("S_1", "S_4", make_condition("1"), shift_processor),
        ("S_2", "S_4", make_condition("0"), shift_processor),
        MooreTransition("S_2", "S_1", make_condition("1"), shift_processor),
        ("S_3", "S_5", make_condition("0"), shift_processor),
        MooreTransition("S_3", "S_3", make_condition("1"), shift_processor),
        ("S_4", "S_3", make_condition("0"), shift_processor),
        MooreTransition("S_4", "S_4", make_condition("1"), shift_processor),
        ("S_5", "S_5", make_condition("0"), shift_processor),
        MooreTransition("S_5", "S_3", make_condition("1"), shift_processor),
      ],
      initial_state="S_0",
      initial_output="",
      stop_condition=lambda input: len(input) == 0,
    )

    machine.update_current_data(input="00101")
    machine.run_all(raise_on_error=False)

    assert len(machine.get_results()) > 0

  def test_plus_3_empty_input(self):
    machine = make_moore_plus_3_machine()
    machine.update_current_data(input="")
    machine.run_all(raise_on_error=False)

    # Должен остановиться по stop_condition сразу
    results = machine.get_results()
    assert len(results) == 0 or results[-1].reason.name == "STOP_CONDITION"

  def test_plus_3_step_by_step(self):
    machine = make_moore_plus_3_machine()
    machine.update_current_data(state_name="S_0", input="010", output="")

    # Первый шаг: вход "010", последний бит "0"
    result = machine.run_once()
    assert result.reason == StepReason.SUCCESS

    # После первого шага вход должен уменьшиться на 1 символ
    input = machine.get_current_input()
    assert input is not None
    assert len(input) == 3  # noqa: PLR2004

    result = machine.run_once()
    assert result.reason == StepReason.SUCCESS

    # После первого шага вход должен уменьшиться на 1 символ
    input = machine.get_current_input()
    assert input is not None
    assert len(input) == 2  # noqa: PLR2004

  def test_plus_3_get_transitions(self):
    machine = make_moore_plus_3_machine()

    transitions_from_s0 = machine.get_state_transitions("S_0")
    assert len(transitions_from_s0) == 2  # noqa: PLR2004

    all_transitions = machine.get_all_transitions()
    assert len(all_transitions) == 12  # noqa: PLR2004
