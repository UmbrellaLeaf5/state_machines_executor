import pytest

from src.state_machines import (
  MealyMachine,
  MealyState,
  MooreMachine,
  MooreState,
)


# ----- Фикстуры для Мили -----


@pytest.fixture
def empty_mealy_machine():
  """Возвращает пустой автомат Мили."""
  return MealyMachine()


@pytest.fixture
def simple_mealy_machine():
  """Возвращает простой автомат Мили с одним состоянием и переходом в себя."""
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


# ----- Фикстуры для Мура -----


@pytest.fixture
def empty_moore_machine():
  """Возвращает пустой автомат Мура."""
  return MooreMachine()


@pytest.fixture
def simple_moore_machine():
  """Возвращает простой автомат Мура с одним состоянием."""
  machine = MooreMachine()

  def cond(input):
    return True

  def output_func(previous_output):
    return previous_output + 1 if isinstance(previous_output, int) else 1

  def proc(input):
    return input + 1 if isinstance(input, int) else 1

  machine.add_state(MooreState("A", output_func, {}))
  machine.add_transition("A", "A", cond, proc)

  return machine
