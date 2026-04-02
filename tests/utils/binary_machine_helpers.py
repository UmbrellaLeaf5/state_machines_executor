from src.state_machines import (
  MealyMachine,
  OutputFunctionProtocol,
  TransConditionProtocol,
)


def make_condition(bit: str) -> TransConditionProtocol[str]:
  """Возвращает условие, которое истинно, если последний бит входной строки равен bit."""

  def condition(input: str) -> bool:
    return input[-1] == bit

  return condition


def make_output_adder(bit: str) -> OutputFunctionProtocol[str]:
  """Возвращает функцию выхода, добавляющую bit в начало предыдущего выхода."""

  def add(previous_output: str) -> str:
    return bit + previous_output

  return add


def shift_processor(input: str) -> str:
  """Удаляет последний символ входной строки."""
  return input[:-1]


def build_transitions_from_dict(
  states_dict: dict,
) -> list:
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
) -> MealyMachine[str, str]:
  """
  Создаёт MealyMachine для бинарных чисел.
  При add_zeros=True добавляет zeros_amount ведущих нулей к входной строке.
  """
  if add_zeros:
    input_str = input_str.zfill(len(input_str) + zeros_amount)

  transitions = build_transitions_from_dict(states_dict)

  return MealyMachine(
    transitions=transitions,
    initial_state=initial_state,
    initial_output="",
    initial_input=input_str,
    stop_condition=lambda input: len(input) == 0,
  )


def run_binary_test(
  states_dict: dict,
  initial_state: str,
  number: int,
  expected: str,
  add_zeros: bool = True,
  zeros_amount: int = 4,
) -> None:
  """Вспомогательная функция для тестирования бинарных автоматов."""
  input_str = bin(number)[2:]
  machine = make_binary_machine(
    states_dict, initial_state, input_str, add_zeros, zeros_amount
  )

  machine.run_all(raise_on_error=False)
  result = machine.get_final_result()

  result = (result.lstrip("0") or "0") if result else "0"

  assert result == expected
