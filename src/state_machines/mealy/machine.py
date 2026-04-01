"""
Модуль с классом автомата Мили.

Предоставляет API для создания, настройки и выполнения автомата.
"""

from .._base.machine import BaseMachine
from ..utils.types import UNSET_TYPE
from ._entity_api import MealyEntityApi
from .state import MealyState, MealyTransition
from .types import MealyStateString, MealyTransitionTuple


class MealyMachine[InputType, OutputType](
  # жесткая связность от:
  MealyEntityApi[InputType, OutputType],
  BaseMachine[
    InputType,
    OutputType,
    MealyState[InputType, OutputType],
    MealyTransition[InputType, OutputType],
    MealyStateString,
    MealyTransitionTuple[InputType, OutputType],
  ],
):
  """
  Автомат Мили.

  Позволяет задать состояния, переходы, выполнять шаги на переходах и получать результаты.
  """

  # --------------------------------------------------------------------------------------

  def _validate_specific(self) -> None:
    """В автомате Мили нет специфичных проверок."""
    pass

  # --------------------------------------------------------------------------------------

  def _execute_state(self) -> OutputType | None:
    """
    В автомате Мили состояние не вычисляет выходное значение.

    Returns:
      Всегда `None`.
    """

    return None

  # --------------------------------------------------------------------------------------

  def _execute_transition(
    self,
    transition: MealyTransition[InputType, OutputType],
    state_output: OutputType | None,
  ) -> OutputType:
    """
    Выполняет функцию выхода перехода.

    Args:
      transition: Объект перехода.
      state_output: Выходное значение состояния (не используется в автомате Мили).

    Returns:
      Результат выполнения функции выхода перехода.

    Raises:
      `RuntimeError`: Если текущее выходное значение не установлено.
    """

    if isinstance(self._current_output, UNSET_TYPE):
      raise RuntimeError("Current output not set")

    return transition.execute(self._current_output, self._function_kwargs)
