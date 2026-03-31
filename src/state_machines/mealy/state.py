"""
Модуль для описания автомата Мили.

Содержит протоколы для колбэков, классы перехода и состояния.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..utils import (
  InputProcessorProtocol,
  OutputFunctionProtocol,
  TransConditionProtocol,
)
from ..utils.types import Kwargs


# MARK: MealyTransition
# --------------------------------------------------------------------------------------


@dataclass
class MealyTransition[InputType, OutputType]:
  """
  Описание перехода в автомате Мили.

  Связывает исходное и целевое состояние, условие, функцию вычисления выхода
  и процессор входа.

  Attributes:
    source_state: Имя исходного состояния.
    target_state: Имя целевого состояния.
    trans_condition: Функция-условие перехода.
    output_function: Функция вычисления выходного значения.
    input_processor: Функция обработки входа.
  """

  source_state: str
  target_state: str

  trans_condition: TransConditionProtocol[InputType]
  output_function: OutputFunctionProtocol[OutputType]
  input_processor: InputProcessorProtocol[InputType]

  # --------------------------------------------------------------------------------------

  def is_transferable(
    self, input: InputType, condition_kwargs: Kwargs | None = None
  ) -> bool:
    """
    Проверяет, можно ли выполнить переход для заданного входа.

    Args:
      input: Входное значение.
      condition_kwargs: Дополнительные аргументы для функции условия.

    Returns:
      `True` если условие выполнено, иначе `False`.
    """

    if condition_kwargs is None:
      condition_kwargs = {}

    return self.trans_condition(input, **condition_kwargs)

  # --------------------------------------------------------------------------------------

  def execute(
    self, previous_output: OutputType, function_kwargs: Kwargs | None = None
  ) -> OutputType:
    """
    Вычисляет выходное значение перехода.

    Args:
      previous_output: Выход предыдущего шага.
      function_kwargs: Дополнительные аргументы для функции выхода.

    Returns:
      Новое выходное значение.
    """

    if function_kwargs is None:
      function_kwargs = {}

    return self.output_function(previous_output, **function_kwargs)

  # --------------------------------------------------------------------------------------

  def process_input(
    self, input: InputType, processor_kwargs: Kwargs | None = None
  ) -> InputType:
    """
    Обрабатывает входное значение.

    Args:
      input: Входное значение.
      processor_kwargs: Дополнительные аргументы для процессора входа.

    Returns:
      Обработанное входное значение.
    """

    if processor_kwargs is None:
      processor_kwargs = {}

    return self.input_processor(input, **processor_kwargs)


# MARK: MealyState
# --------------------------------------------------------------------------------------


@dataclass
class MealyState[InputType, OutputType]:
  """
  Состояние автомата Мили.

  Содержит имя состояния и словарь переходов в другие состояния.

  Attributes:
    name: Имя состояния.
    transitions: Словарь переходов, где ключ - имя целевого состояния,
                  значение - объект MealyTransition.
  """

  name: str

  transitions: dict[str, MealyTransition[InputType, OutputType]]

  # --------------------------------------------------------------------------------------

  def has_transition(self, target_state: str) -> bool:
    """
    Проверяет, есть ли переход в указанное состояние.

    Args:
      target_state: Имя целевого состояния.

    Returns:
      `True` если переход существует, иначе `False`.
    """

    return target_state in self.transitions

  # --------------------------------------------------------------------------------------

  def add_transition(self, transition: MealyTransition[InputType, OutputType]) -> None:
    """
    Добавляет переход.

    Args:
      transition: Объект перехода.

    Raises:
      `ValueError`: Если source_state не совпадает с именем состояния
                  или переход в target_state уже существует.
    """

    if transition.source_state != self.name:
      raise ValueError(
        f"Invalid transition.source_state: {transition.source_state} != {self.name}"
      )

    if self.has_transition(transition.target_state):
      raise ValueError(
        f"Transition from '{self.name}' to '{transition.target_state}' already exists. "
        "Only one transition per target state is allowed."
      )

    self.transitions[transition.target_state] = transition

  # --------------------------------------------------------------------------------------

  def replace_transition(
    self, transition: MealyTransition[InputType, OutputType]
  ) -> None:
    """
    Заменяет существующий переход.

    Args:
      transition: Новый объект перехода.

    Raises:
      `ValueError`: Если source_state не совпадает с именем состояния
                  или переход в target_state не существует.
    """

    if transition.source_state != self.name:
      raise ValueError(
        f"Invalid transition.source_state: {transition.source_state} != {self.name}"
      )

    if transition.target_state not in self.transitions:
      raise ValueError(
        f"Transition from '{self.name}' to '{transition.target_state}' "
        "does not exist, cannot replace."
      )

    self.transitions[transition.target_state] = transition

  # --------------------------------------------------------------------------------------

  def remove_transition(self, target_state: str) -> None:
    """
    Удаляет переход в указанное состояние.

    Args:
      target_state: Имя целевого состояния.

    Raises:
      `KeyError`: Если переход не существует.
    """

    if target_state not in self.transitions:
      raise KeyError(f"Transition from '{self.name}' to '{target_state}' not found")

    self.transitions.pop(target_state)

  # --------------------------------------------------------------------------------------

  def get_available_transitions(
    self, input: InputType, condition_kwargs: Kwargs | None = None
  ) -> list[MealyTransition[InputType, OutputType]]:
    """
    Возвращает список переходов, доступных для заданного входа.

    Args:
      input: Входное значение.
      condition_kwargs: Дополнительные аргументы для функций условий.

    Returns:
      Список переходов, для которых условие выполнено.
    """

    if condition_kwargs is None:
      condition_kwargs = {}

    return [
      transition
      for transition in self.transitions.values()
      if transition.is_transferable(input, condition_kwargs)
    ]
