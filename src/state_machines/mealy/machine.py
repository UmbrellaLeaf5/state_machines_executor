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
    pass

  # --------------------------------------------------------------------------------------

  def _execute_state(self) -> OutputType | None:
    return None

  # --------------------------------------------------------------------------------------

  def _execute_transition(
    self,
    transition: MealyTransition[InputType, OutputType],
    state_output: OutputType | None,
  ) -> OutputType:
    if isinstance(self._current_output, UNSET_TYPE):
      raise RuntimeError("Current output not set")

    return transition.execute(self._current_output, self._function_kwargs)
