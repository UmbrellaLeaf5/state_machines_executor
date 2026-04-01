"""
Модуль с классом автомата Мура.

Предоставляет API для создания, настройки и выполнения автомата.
"""

from .._base.machine import BaseMachine
from ..utils.types import UNSET_TYPE
from ._entity_api import MooreEntityApi
from .state import MooreState, MooreTransition
from .types import MooreStateTuple, MooreTransitionTuple


class MooreMachine[InputType, OutputType](
  # жесткая связность от:
  MooreEntityApi[InputType, OutputType],
  BaseMachine[
    InputType,
    OutputType,
    MooreState[InputType, OutputType],
    MooreTransition[InputType],
    MooreStateTuple[OutputType],
    MooreTransitionTuple[InputType],
  ],
):
  """
  Автомат Мура.

  Позволяет задать состояния с привязанными выходами, переходы,
  выполнять шаги и получать результаты.
  """

  # --------------------------------------------------------------------------------------

  def _validate_specific(self) -> None:
    missing_output_functions = [
      state_name
      for state_name, state in self._states.items()
      if state.output_function is None
    ]

    if missing_output_functions:
      msg = "States without output function:\n" + "\n".join(
        f"  '{state_name}'" for state_name in missing_output_functions
      )

      raise ValueError(msg)

  # --------------------------------------------------------------------------------------

  def _execute_state(self) -> OutputType | None:
    if isinstance(self._current_state, UNSET_TYPE):
      raise RuntimeError("Current state not set")

    if isinstance(self._current_output, UNSET_TYPE):
      raise RuntimeError("Current output not set")

    return self._current_state.execute(self._current_output, self._function_kwargs)

  # --------------------------------------------------------------------------------------

  def _execute_transition(
    self, transition: MooreTransition[InputType], state_output: OutputType | None
  ) -> OutputType:
    if state_output is None:
      raise RuntimeError("Moore machine: state_output cannot be None")

    return state_output
