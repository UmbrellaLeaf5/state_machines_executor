from abc import ABC

from ..utils.types import Kwargs
from .transition import BaseTransition


class BaseState[InputType, TransitionType: BaseTransition](ABC):
  """
  Базовый протокол состояния.

  Определяет минимальный интерфейс для состояния в автомате.
  """

  name: str
  transitions: dict[str, TransitionType]

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

  def add_transition(self, transition: TransitionType) -> None:
    """
    Добавляет переход.

    Args:
      transition: Объект перехода.

    Raises:
      `ValueError`: Если переход в `target_state` уже существует.
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

  def replace_transition(self, transition: TransitionType) -> None:
    """
    Заменяет существующий переход.

    Args:
      transition: Новый объект перехода.

    Raises:
      `ValueError`: Если переход в `target_state` не существует.
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
  ) -> list[TransitionType]:
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
