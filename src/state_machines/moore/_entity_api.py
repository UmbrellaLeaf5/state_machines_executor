"""
Миксин для управления сущностями автомата Мура.

Содержит методы для работы с состояниями, переходами, текущими данными,
общими kwargs, условием остановки и результатами.
"""

from .._base import BaseEntityApi
from ..utils.protocols import (
  InputProcessorProtocol,
  OutputFunctionProtocol,
  StopConditionProtocol,
  TransConditionProtocol,
)
from ..utils.types import UNSET_VAL, Kwargs
from .state import MooreState
from .transition import MooreTransition
from .types import MooreStateTuple, MooreTransitionTuple


# IMP: идеология методов:
#
# если есть entity, то есть:
# 1. def add_entity(self, ...) -> None: ...
# 2. def remove_entity(self, ...) -> None: ...
#
# если есть entities, то есть:
# 1. def set_entities(self, ...) -> None: self.clear_entities(); self.add_entities(...)
# 2. def update_entities(self, ...) -> None: ...
# 3. def clear_entities(self, ...) -> None: ...


class MooreEntityApi[InputType, OutputType](
  BaseEntityApi[
    InputType,
    OutputType,
    MooreState[InputType, OutputType],
    MooreTransition[InputType],
    MooreStateTuple[OutputType],
    MooreTransitionTuple[InputType],
  ]
):
  """
  Миксин, предоставляющий API для управления сущностями автомата Мура.
  """

  # MARK: Init
  # --------------------------------------------------------------------------------------

  def __init__(
    self,
    states: list[MooreStateTuple[OutputType] | MooreState[InputType, OutputType]]
    | None = None,
    transitions: list[MooreTransitionTuple[InputType] | MooreTransition[InputType]]
    | None = None,
    initial_state: str | None = None,
    initial_output: OutputType | None = None,
    initial_input: InputType | None = None,
    stop_condition: StopConditionProtocol[InputType] | None = None,
    stop_condition_kwargs: Kwargs | None = None,
    condition_kwargs: Kwargs | None = None,
    function_kwargs: Kwargs | None = None,
    processor_kwargs: Kwargs | None = None,
  ) -> None:
    """
    Создаёт автомат Мура.

    Автомат можно настроить полностью при создании или добавлять состояния
    и переходы позже через соответствующие методы.

    Args:
        states: Список состояний. Каждый элемент может быть:
            - кортежем `(name, output_function)` - для быстрого создания состояния
            - объектом `MooreState` - если состояние уже сконфигурировано

        transitions: Список переходов. Каждый элемент может быть:
            - кортежем из четырёх элементов: `(
            source_state, target_state, condition, processor)`
            - объектом `MooreTransition`

        initial_state: Имя начального состояния.
            Если указан, автомат будет готов к запуску после установки
            `initial_output` и `initial_input`.

        initial_output: Начальное выходное значение.
            Используется вместе с `initial_state`.

        initial_input: Начальное входное значение.
            Используется вместе с `initial_state`.

        stop_condition: Функция-условие остановки.
            Вызывается перед каждым шагом выполнения.
            Принимает текущий вход и возвращает `True` для остановки автомата.
            Результат шага в этом случае будет иметь `reason = STOP_CONDITION`.

        stop_condition_kwargs: Дополнительные именованные аргументы для `stop_condition`.
            Передаются в функцию как `**kwargs` при каждом вызове.

        condition_kwargs: Дополнительные именованные аргументы для всех условий переходов.
            Передаются в каждую функцию `condition` как `**kwargs`.

        function_kwargs: Доп. именованные аргументы для всех функций выхода состояний.
            Передаются в каждую `output_function` как `**kwargs`.

        processor_kwargs: Дополнительные именованные аргументы для всех процессоров входа.
            Передаются в каждый `input_processor` как `**kwargs`.
    """

    self._states = {}
    self._results = []

    self._current_state = UNSET_VAL
    self._current_output = UNSET_VAL
    self._current_input = UNSET_VAL

    self._condition_kwargs = {}
    self._function_kwargs = {}
    self._processor_kwargs = {}

    self._stop_condition = None
    self._stop_condition_kwargs = {}

    # IMP: тут используются update, а не set, потому что еще ничего не проинициализировано

    if states is not None:
      self.update_states(states)

    if transitions is not None:
      self.update_transitions(transitions)

    if (
      condition_kwargs is not None
      or function_kwargs is not None
      or processor_kwargs is not None
    ):
      self.update_common_kwargs(
        condition_kwargs=condition_kwargs,
        function_kwargs=function_kwargs,
        processor_kwargs=processor_kwargs,
      )

    if stop_condition is not None:
      self.add_stop_condition(stop_condition, stop_condition_kwargs)

    if (
      initial_state is not None or initial_output is not None or initial_input is not None
    ):
      self.update_current_data(initial_state, initial_input, initial_output)

  # MARK: States
  # --------------------------------------------------------------------------------------

  def _adapt_state(
    self, item: MooreStateTuple | MooreState[InputType, OutputType]
  ) -> tuple[str, MooreState[InputType, OutputType]]:
    name: str
    state: MooreState[InputType, OutputType]

    if isinstance(item, tuple):
      if len(item) != 2:  # noqa: PLR2004
        raise ValueError(f"Expected tuple of `(name, output_function)`, got {item}")

      name, output_function = item

      if not isinstance(name, str):
        raise TypeError(f"State name must be `str`, got `{type(name)}`")

      state = MooreState(name, output_function, {})

    elif isinstance(item, MooreState):
      state = item
      name = state.name

    else:
      raise TypeError(
        f"Expected `tuple[str, OutputFunctionProtocol]` or `MooreState`, "
        f"got `{type(item).__name__}`"
      )

    return (name, state)

  # MARK: Transitions
  # --------------------------------------------------------------------------------------

  def add_transition(
    self,
    source_state: str,
    target_state: str,
    trans_condition: TransConditionProtocol[InputType],
    input_processor: InputProcessorProtocol[InputType],
    replace: bool = False,
  ) -> None:
    """
    Добавляет переход.

    Args:
      source_state: Имя исходного состояния.
      target_state: Имя целевого состояния.
      trans_condition: Функция-условие.
      input_processor: Функция обработки входа.
      replace: Если `True` и переход уже существует, он заменяется.
        Если `False` и переход существует, вызывается `ValueError`.

    Raises:
      `KeyError`: Если исходное или целевое состояние не существует.
      `ValueError`: Если переход уже существует и `replace=False`.
    """

    self._add_transition(
      source_state,
      target_state,
      trans_condition,
      None,
      input_processor,
      replace,
    )

  # --------------------------------------------------------------------------------------

  def add_transition_entity(
    self,
    transition: MooreTransitionTuple[InputType] | MooreTransition[InputType],
    replace: bool = False,
  ) -> None:
    """
    Добавляет переход из готового объекта или кортежа.

    Args:
        transition: Объект MooreTransition или кортеж из 4 элементов.
        replace: Заменять существующий переход или нет.

    Raises:
      `ValueError`: Если переход уже существует и `replace=False`.
      `TypeError`: Если передан неподдерживаемый тип.
    """

    if isinstance(transition, MooreTransition):
      self._add_transition_entity(transition, replace)

    elif isinstance(transition, tuple):
      self._add_transition_tuple(transition, 4, replace)

    else:
      raise TypeError(f"Expected {MooreTransition} or tuple, got {type(transition)}")

  # --------------------------------------------------------------------------------------

  def _ensure_state_exists(self, state_name: str) -> None:
    if state_name not in self._states:
      raise KeyError(
        f"Source state '{state_name}' not found. "
        f"Add it first using add_state() or set_states()."
      )

  # --------------------------------------------------------------------------------------

  def _create_transition(
    self,
    source_state: str,
    target_state: str,
    trans_condition: TransConditionProtocol[InputType],
    output_function: OutputFunctionProtocol[OutputType] | None,
    input_processor: InputProcessorProtocol[InputType],
  ) -> MooreTransition[InputType]:
    """
    Создаёт объект перехода.

    Args:
      source_state: Имя исходного состояния.
      target_state: Имя целевого состояния.
      trans_condition: Функция-условие перехода.
      output_function: Функция вычисления выхода (None для автомата Мура).
      input_processor: Функция обработки входа.

    Returns:
      Объект `MooreTransition`.
    """

    return MooreTransition(
      source_state=source_state,
      target_state=target_state,
      trans_condition=trans_condition,
      input_processor=input_processor,
    )
