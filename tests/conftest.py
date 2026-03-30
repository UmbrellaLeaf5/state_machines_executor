import pytest

from src.state_machines import MealyMachine, MealyState


@pytest.fixture
def empty_machine():
  """Возвращает пустой автомат Мили."""
  return MealyMachine()


@pytest.fixture
def simple_machine():
  """Возвращает простой автомат с одним состоянием и переходом в себя."""
  machine = MealyMachine()

  def cond(input):
    return True

  def func(previous_output):
    return previous_output + 1 if isinstance(previous_output, int) else 1

  def proc(input):
    return input + 1 if isinstance(input, int) else 1

  machine.add_state(MealyState("A", {}))
  machine.add_transition("A", "A", cond, func, proc)

  return machine


@pytest.fixture
def machine_with_two_states():
  """Возвращает автомат с двумя состояниями, переключающимися между собой."""
  machine = MealyMachine()

  def cond(input):
    return True

  def func(previous_output):
    return previous_output

  def proc(input):
    return input

  machine.add_state(MealyState("A", {}))
  machine.add_state(MealyState("B", {}))
  machine.add_transition("A", "B", cond, func, proc)
  machine.add_transition("B", "A", cond, func, proc)

  return machine
