"""
Модуль с классом автомата Мура.

Предоставляет API для создания, настройки и выполнения автомата.
"""

import warnings
from collections.abc import Callable

from ..utils import UNSET, StepData, StepReason, StepResult
from ._entity_api import MooreEntityApi
from .state import MooreTransition


class MooreMachine[InputType, OutputType](
  # жесткая связность от:
  MooreEntityApi[InputType, OutputType]
):
  """
  Автомат Мура.

  Позволяет задать состояния с привязанными выходами, переходы,
  выполнять шаги и получать результаты.
  """

  # MARK: Helpers
  # --------------------------------------------------------------------------------------

  def reset_execution(
    self, also_reset_kwargs: bool = False, also_reset_stop_condition: bool = False
  ) -> None:
    """
    Сбрасывает состояние выполнения автомата.

    Args:
      also_reset_kwargs: Если `True`, также очищает все `common kwargs`.
      also_reset_stop_condition: Если `True`, также удаляет условие остановки.
    """

    self.clear_current_data()
    self.clear_results()

    if also_reset_kwargs:
      self.clear_common_kwargs()

    if also_reset_stop_condition:
      self.remove_stop_condition()

  # --------------------------------------------------------------------------------------

  def validate(self) -> None:
    """
    Проверяет целостность автомата.

    Raises:
      `ValueError`: если какое-либо целевое состояние,
        указанное в переходах, отсутствует в списке состояний,
        или если у какого-либо состояния не задана функция выхода.
    """

    missing_targets = [
      (source_name, target_name)
      for source_name, state in self._states.items()
      for target_name in state.transitions
      if target_name not in self._states
    ]

    if missing_targets:
      msg = "Missing target states:\n" + "\n".join(
        f"  from '{src}' to '{tgt}'" for src, tgt in missing_targets
      )

      raise ValueError(msg)

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

  def _format_ambiguous_error(
    self, available_transitions: list[MooreTransition[InputType]]
  ) -> str:
    """
    Формирует сообщение об ошибке неоднозначности перехода.

    Args:
      available_transitions: Список переходов, которые одновременно доступны.

    Returns:
      Отформатированное сообщение с деталями.
    """

    if isinstance(self._current_state, UNSET):
      raise RuntimeError("Current state not set")

    def _get_name(obj: Callable) -> str:
      return getattr(obj, "__name__", repr(obj))

    transitions_desc = [
      f"  to '{t.target_state}' with:\n"
      f"    condition: '{_get_name(t.trans_condition)}'\n"
      f"    processor: '{_get_name(t.input_processor)}'"
      for t in available_transitions
    ]

    return (
      f"Ambiguous transition: {len(available_transitions)} transitions available.\n"
      f"Current state: '{self._current_state.name}'\n"
      f"Current input: '{self._current_input}'\n"
      f"Current output: '{self._current_output}'\n"
      f"Condition kwargs: {self._condition_kwargs}\n"
      "Transitions:\n" + "\n".join(transitions_desc)
    )

  # MARK: Run
  # --------------------------------------------------------------------------------------

  def run_once(self) -> StepResult[InputType, OutputType]:
    """
    Выполняет один шаг автомата.

    Returns:
      Результат шага с указанием причины завершения и данными (если успешно).

    Raises:
      `RuntimeError`: Если текущие данные не установлены.
      `ValueError`: Если найдено несколько доступных переходов (неоднозначность).
      `KeyError`: Если целевое состояние не существует.
    """

    if isinstance(self._current_state, UNSET):
      raise RuntimeError("Current state not set")

    if isinstance(self._current_output, UNSET):
      raise RuntimeError("Current output not set")

    if isinstance(self._current_input, UNSET):
      raise RuntimeError("Current input not set")

    # IMP: идеологически:
    # if not self.is_ready():
    #   raise RuntimeError(...)
    # (но нужно сужение типов, поэтому не используем)

    if self._stop_condition and self._stop_condition(
      self._current_input, **self._stop_condition_kwargs
    ):
      return StepResult[InputType, OutputType](reason=StepReason.STOP_CONDITION)

    output = self._current_state.execute(self._current_output, self._function_kwargs)

    available_transitions = self._current_state.get_available_transitions(
      self._current_input, self._condition_kwargs
    )

    if not available_transitions:
      warnings.warn(
        f"No transitions in state '{self._current_state.name}' "
        f"at input '{self._current_input}' "
        f"with previous output '{self._current_output}'",
        UserWarning,
        stacklevel=2,
      )

      return StepResult[InputType, OutputType](reason=StepReason.NO_TRANSITION)

    if len(available_transitions) > 1:
      raise RuntimeError(self._format_ambiguous_error(available_transitions))

    transition = available_transitions[0]

    target_state = self._states.get(transition.target_state)
    if target_state is None:
      raise KeyError(
        f"Target state '{transition.target_state}' not found in machine states"
      )

    processed_input = transition.process_input(
      self._current_input, self._processor_kwargs
    )

    self._current_state = target_state
    self._current_output = output
    self._current_input = processed_input

    moore_step = StepResult(
      reason=StepReason.SUCCESS,
      data=StepData.from_tuple((processed_input, output)),
    )

    self._results.append(moore_step)
    return moore_step

  # --------------------------------------------------------------------------------------

  def run_all(
    self,
    clear_before_run: bool = False,
    raise_on_error: bool = True,
  ) -> list[StepResult[InputType, OutputType]]:
    """
    Выполняет автомат до остановки (по условию или отсутствию переходов).

    Args:
      clear_before_run: Если `True`, очищает историю результатов перед запуском.
        Если `False`, добавляет новые шаги к существующим.
      raise_on_error: Если `True`, падает с исключением, проходя по циклу.
        Если `False`, завершается на исключении, добавляя в историю
        шаг с причиной `EXCEPTION`
        (c ошибками валидации графа всё равно будет падать!).

    Returns:
      Список шагов выполнения.
    """

    self.validate()

    if clear_before_run:
      self.clear_results()

    while True:
      try:
        step_result = self.run_once()

      except Exception as e:
        if raise_on_error:
          raise e

        self._results.append(StepResult[InputType, OutputType].error_step(e))
        break

      if step_result.reason != StepReason.SUCCESS:
        self._results.append(step_result)  # добавление ошибочного step
        break

    return self.get_results()
