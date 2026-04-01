import dataclasses
import typing
import warnings
from abc import ABC, abstractmethod

from ..utils.protocols import (
  InputProcessorProtocol,
  OutputFunctionProtocol,
  StopConditionProtocol,
  TransConditionProtocol,
)
from ..utils.step import StepData, StepReason, StepResult
from ..utils.types import (
  UNSET_TYPE,
  UNSET_VAL,
  Kwargs,
  ResultTuple,
)
from .state import BaseState
from .transition import BaseTransition


class BaseEntityApi[
  InputType,
  OutputType,
  StateType: BaseState,
  TransitionType: BaseTransition,
  PresentedStateType: str | tuple,
  PresentedTransitionType: tuple,
](ABC):
  """
  Базовый класс для управления сущностями автоматов Мили и Мура.
  """

  # MARK: Fields
  # --------------------------------------------------------------------------------------

  _states: dict[str, StateType]
  _results: list[StepResult[InputType, OutputType]]

  _current_state: StateType | UNSET_TYPE
  _current_output: OutputType | UNSET_TYPE
  _current_input: InputType | UNSET_TYPE

  _condition_kwargs: Kwargs
  _function_kwargs: Kwargs
  _processor_kwargs: Kwargs

  _stop_condition: StopConditionProtocol[InputType] | None
  _stop_condition_kwargs: Kwargs

  # MARK: States
  # --------------------------------------------------------------------------------------

  def get_state_names(self) -> list[str]:
    """Возвращает список имён всех состояний (копия)."""

    return list(self._states.keys())

  # --------------------------------------------------------------------------------------

  def get_states_amount(self) -> int:
    """Возвращает количество состояний."""

    return len(self._states)

  # --------------------------------------------------------------------------------------
  # !: entity

  def add_state(self, state: StateType) -> None:
    """
    Добавляет состояние.

    Args:
      state: Объект состояния.

    Raises:
      `ValueError`: Если состояние с таким именем уже существует.
    """

    if state.name in self._states:
      raise ValueError(f"State '{state.name}' already exists")

    self._states[state.name] = state

  # --------------------------------------------------------------------------------------

  def remove_state(self, state_name: str, cleanup_transitions: bool = False) -> None:
    """
    Удаляет состояние.

    Args:
      state_name: Имя удаляемого состояния.
      cleanup_transitions: Если `True`, удаляет все переходы, связ. с этим состоянием:
        - переходы из других состояний в это состояние,
        - переходы из этого состояния в другие состояния.

    Raises:
      `KeyError`: Если состояние не существует.
    """

    if state_name not in self._states:
      raise KeyError(f"State '{state_name}' is not found")

    if (
      not isinstance(self._current_state, UNSET_TYPE)
      and self._current_state.name == state_name
    ):
      warnings.warn(
        f"Removing current state '{state_name}', machine reset",
        UserWarning,
        stacklevel=2,
      )

      self.clear_current_data()

    if cleanup_transitions:
      for state in self._states.values():
        if state_name in state.transitions:
          state.remove_transition(state_name)

      self._states[state_name].transitions.clear()

    self._states.pop(state_name)

  # --------------------------------------------------------------------------------------
  # !: entities

  def set_states(self, states: list[PresentedStateType | StateType]) -> None:
    self.clear_states()
    self.update_states(states)

  # --------------------------------------------------------------------------------------

  def update_states(self, states: list[PresentedStateType | StateType]) -> None:
    items: list[StateType] = []
    seen_names: set[str] = set()

    for item in states:
      name, state = self._parse_state(item)

      # проверяем дубликаты в списке
      if name in seen_names:
        raise ValueError(f"Duplicate state name in input: {name}")

      seen_names.add(name)

      # проверяем, что состояние не существует в автомате
      if name in self._states:
        raise ValueError(f"State '{name}' already exists")

      items.append(state)

    for state in items:
      self._states[state.name] = state

  @abstractmethod
  def _parse_state(self, item: PresentedStateType | StateType) -> tuple[str, StateType]:
    """
    Преобразует элемент входного списка в кортеж (имя состояния, объект состояния).
    Должен выбрасывать TypeError/ValueError при некорректном формате.
    """

  # --------------------------------------------------------------------------------------

  def clear_states(self) -> None:
    """Удаляет все состояния."""

    self._states.clear()

  # MARK: Transitions
  # --------------------------------------------------------------------------------------

  def get_state_transitions(self, state_name: str) -> list[PresentedTransitionType]:
    if state_name not in self._states:
      raise KeyError(f"State '{state_name}' not found")

    state = self._states[state_name]

    return [
      typing.cast(PresentedTransitionType, dataclasses.astuple(trans))
      for trans in state.transitions.values()
    ]

  # --------------------------------------------------------------------------------------

  def get_state_transitions_amount(self, state_name: str) -> int:
    """
    Возвращает количество переходов из указанного состояния.

    Args:
      state_name: Имя состояния.

    Returns:
      Количество переходов.

    Raises:
      `KeyError`: Если состояние не существует.
    """

    if state_name not in self._states:
      raise KeyError(f"State '{state_name}' not found")

    return len(self._states[state_name].transitions)

  # --------------------------------------------------------------------------------------

  def get_all_transitions(
    self,
  ) -> list[PresentedTransitionType]:
    return [
      typing.cast(PresentedTransitionType, dataclasses.astuple(trans))
      for state in self._states.values()
      for trans in state.transitions.values()
    ]

  # --------------------------------------------------------------------------------------

  def get_all_transitions_amount(self) -> int:
    """Возвращает общее количество переходов во всех состояниях."""

    return sum(len(state.transitions) for state in self._states.values())

  # --------------------------------------------------------------------------------------
  # !: entity

  @abstractmethod
  def add_transition(self, *args, **kwargs) -> None:
    pass

  def _add_transition(
    self,
    source_state: str,
    target_state: str,
    condition: TransConditionProtocol[InputType],
    output_function: OutputFunctionProtocol[OutputType] | None,
    input_processor: InputProcessorProtocol[InputType],
    replace: bool = False,
  ) -> None:
    self._ensure_state_exists(source_state)
    self._ensure_state_exists(target_state)

    transition = self._create_transition(
      source_state, target_state, condition, output_function, input_processor
    )

    source = self._states[source_state]

    if source.has_transition(target_state):
      if not replace:
        raise ValueError(
          f"Transition from '{source_state}' to '{target_state}' already exists. "
          "Use `replace=True` to replace it."
        )

      source.replace_transition(transition)

    else:
      source.add_transition(transition)

  @abstractmethod
  def _ensure_state_exists(self, state_name: str) -> None:
    """Гарантирует, что состояние существует.
    Для Мили - создаёт, для Мура - выбрасывает ошибку."""
    pass

  @abstractmethod
  def _create_transition(
    self,
    source_state: str,
    target_state: str,
    trans_condition: TransConditionProtocol[InputType],
    output_function: OutputFunctionProtocol[OutputType] | None,
    input_processor: InputProcessorProtocol[InputType],
  ) -> TransitionType:
    """Создаёт объект перехода (для Мили output_func обязателен, для Мура - None)."""
    pass

  # --------------------------------------------------------------------------------------

  def remove_transition(self, source_state: str, target_state: str) -> None:
    """
    Удаляет переход.

    Args:
      source_state: Имя исходного состояния.
      target_state: Имя целевого состояния.

    Raises:
      `KeyError`: Если исходное состояние не существует или переход не найден.
    """

    if source_state not in self._states:
      raise KeyError(f"State '{source_state}' is not found")

    state = self._states[source_state]

    if target_state not in state.transitions:
      raise KeyError(f"Transition from '{source_state}' to '{target_state}' is not found")

    state.remove_transition(target_state)

  # --------------------------------------------------------------------------------------
  # !: entities

  def set_transitions(
    self,
    transitions: list[PresentedTransitionType],
  ) -> None:
    self.clear_transitions()
    self.update_transitions(transitions)

  # --------------------------------------------------------------------------------------

  def update_transitions(
    self,
    transitions: list[PresentedTransitionType],
  ) -> None:
    for trans in transitions:
      self.add_transition(*trans)

  # --------------------------------------------------------------------------------------

  def clear_transitions(self) -> None:
    """Удаляет все переходы из всех состояний."""

    for state in self._states.values():
      state.transitions.clear()

  # MARK: Current data
  # --------------------------------------------------------------------------------------

  def get_current_state_name(self) -> str | None:
    """Возвращает имя текущего состояния или `None`, если оно не установлено."""

    if isinstance(self._current_state, UNSET_TYPE):
      return None

    return self._current_state.name

  # --------------------------------------------------------------------------------------

  def get_current_output(self) -> OutputType | None:
    """Возвращает текущее выходное значение или `None`, если оно не установлено."""

    if isinstance(self._current_output, UNSET_TYPE):
      return None

    return self._current_output

  # --------------------------------------------------------------------------------------

  def get_current_input(self) -> InputType | None:
    """Возвращает текущее входное значение или `None`, если оно не установлено."""

    if isinstance(self._current_input, UNSET_TYPE):
      return None

    return self._current_input

  # --------------------------------------------------------------------------------------

  def is_ready(self) -> bool:
    """Проверяет, что автомат готов к запуску (установлены состояние, выход и вход)."""

    return not (
      isinstance(self._current_state, UNSET_TYPE)
      or isinstance(self._current_output, UNSET_TYPE)
      or isinstance(self._current_input, UNSET_TYPE)
    )

  # --------------------------------------------------------------------------------------
  # !: entities

  def set_current_data(
    self,
    state_name: str,
    input: InputType,
    output: OutputType,
  ) -> None:
    """
    Устанавливает все компоненты текущего состояния.

    Args:
      state_name: Имя состояния.
      input: Входное значение.
      output: Выходное значение.
    """

    self.clear_current_data()
    self.update_current_data(state_name, input, output)

  # --------------------------------------------------------------------------------------

  def update_current_data(
    self,
    state_name: str | None = None,
    input: InputType | None = None,
    output: OutputType | None = None,
  ) -> None:
    """
    Частично обновляет текущие данные.

    Можно обновить только состояние, только выход, только вход или любую комбинацию.

    Примечание: Для `is_ready()` требуются все три компонента.
    Если обновить только выход или вход без состояния, автомат не будет готов к запуску.

    Args:
      state_name: Имя состояния (или `None`, чтобы не обновлять).
      input: Входное значение (или `None`, чтобы не обновлять).
      output: Выходное значение (или `None`, чтобы не обновлять).

    Raises:
      `KeyError`: Если `state_name` передан, но состояние не существует.
    """

    if state_name is not None:
      if state_name not in self._states:
        raise KeyError(f"State '{state_name}' not found")

      self._current_state = self._states[state_name]

    if output is not None:
      self._current_output = output

    if input is not None:
      self._current_input = input

  # --------------------------------------------------------------------------------------

  def clear_current_data(self) -> None:
    """Сбрасывает текущие данные в состояние 'не установлено'"""

    self._current_state = UNSET_VAL
    self._current_output = UNSET_VAL
    self._current_input = UNSET_VAL

  # MARK: Common kwargs
  # --------------------------------------------------------------------------------------
  # !: entities

  def set_common_kwargs(
    self,
    condition_kwargs: Kwargs | None = None,
    function_kwargs: Kwargs | None = None,
    processor_kwargs: Kwargs | None = None,
  ) -> None:
    """
    Заменяет все common `kwargs` новыми словарями.

    Args:
      condition_kwargs: Новый словарь для условий.
      function_kwargs: Новый словарь для функций выхода.
      processor_kwargs: Новый словарь для процессоров входа.
    """

    self.clear_common_kwargs()
    self.update_common_kwargs(condition_kwargs, function_kwargs, processor_kwargs)

  # --------------------------------------------------------------------------------------

  def update_common_kwargs(
    self,
    condition_kwargs: Kwargs | None = None,
    function_kwargs: Kwargs | None = None,
    processor_kwargs: Kwargs | None = None,
  ) -> None:
    """
    Обновляет common `kwargs` (добавляет или перезаписывает ключи).

    Args:
      condition_kwargs: Словарь для обновления условий.
      function_kwargs: Словарь для обновления функций выхода.
      processor_kwargs: Словарь для обновления процессоров входа.
    """

    if condition_kwargs is not None:
      self._condition_kwargs.update(condition_kwargs)

    if function_kwargs is not None:
      self._function_kwargs.update(function_kwargs)

    if processor_kwargs is not None:
      self._processor_kwargs.update(processor_kwargs)

  # --------------------------------------------------------------------------------------

  def clear_common_kwargs(self) -> None:
    """Очищает все `common kwargs`."""

    self._condition_kwargs = {}
    self._function_kwargs = {}
    self._processor_kwargs = {}

  # MARK: Stop condition
  # --------------------------------------------------------------------------------------
  # !: entity

  def add_stop_condition(
    self,
    stop_condition: StopConditionProtocol[InputType],
    stop_condition_kwargs: Kwargs | None = None,
  ) -> None:
    """
    Устанавливает условие остановки.

    Args:
      stop_condition: Функция, принимающая вход и возвращающая `True` для остановки.
      stop_condition_kwargs: Дополнительные аргументы для `stop_condition`.
    """

    if stop_condition_kwargs is None:
      stop_condition_kwargs = {}

    self._stop_condition = stop_condition
    self._stop_condition_kwargs = stop_condition_kwargs

  # --------------------------------------------------------------------------------------

  def remove_stop_condition(self) -> None:
    """Удаляет условие остановки."""

    self._stop_condition = None
    self._stop_condition_kwargs = {}

  # MARK: Results
  # --------------------------------------------------------------------------------------

  def get_results(self) -> list[StepResult[InputType, OutputType]]:
    """Возвращает копию списка всех шагов."""

    return self._results.copy()

  # --------------------------------------------------------------------------------------

  def get_results_data(self) -> list[StepData[InputType, OutputType]]:
    """Возвращает копии данных всех шагов."""

    return [
      StepData(step.data.processed_input, step.data.output) for step in self._results
    ]

  # --------------------------------------------------------------------------------------

  def get_results_tuple(self) -> list[ResultTuple[InputType, OutputType]]:
    """Возвращает список кортежей `(input, output)` для всех шагов."""

    return [(step.data.processed_input, step.data.output) for step in self._results]

  # --------------------------------------------------------------------------------------

  def get_only_results(self) -> list[OutputType | None]:
    """Возвращает список выходных значений для всех шагов."""

    return [step.data.output for step in self._results]

  # --------------------------------------------------------------------------------------

  def get_final_result(self) -> OutputType | None:
    """Возвращает выходное значение последнего успешного шага или `None`."""

    for step in reversed(self._results):
      if step.reason == StepReason.SUCCESS:
        return step.data.output

    return None

  # --------------------------------------------------------------------------------------

  def clear_results(self) -> None:
    """Очищает историю результатов выполнения."""

    self._results.clear()
