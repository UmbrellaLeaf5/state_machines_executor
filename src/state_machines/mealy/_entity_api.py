"""
Миксин для управления сущностями автомата Мили.

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
from .state import MealyState
from .transition import MealyTransition
from .types import MealyStateString, MealyTransitionTuple


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


class MealyEntityApi[InputType, OutputType](
  BaseEntityApi[
    InputType,
    OutputType,
    MealyState[InputType, OutputType],
    MealyTransition[InputType, OutputType],
    MealyStateString,
    MealyTransitionTuple[InputType, OutputType],
  ]
):
  """
  Миксин, предоставляющий API для управления сущностями автомата Мили.
  """

  # MARK: Init
  # --------------------------------------------------------------------------------------

  def __init__(
    self,
    transitions: list[
      MealyTransitionTuple[InputType, OutputType] | MealyTransition[InputType, OutputType]
    ]
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
    Создаёт автомат Мили.

    Все параметры необязательны. Если не переданы, автомат настраивается позже
    через соответствующие методы.

    Args:
        transitions: Список переходов. Каждый элемент может быть:
            - кортежем из пяти элементов: `(
              source_state, target_state, condition, function, processor)`
            - объектом `MealyTransition`

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
            Передаются в функцию как `**kwargs`.

        condition_kwargs: Дополнительные именованные аргументы для всех условий переходов.
            Передаются в каждую condition как `**kwargs`.

        function_kwargs: Доп. именованные аргументы для всех функций вычисления выхода.
            Передаются в каждую function как `**kwargs`.

        processor_kwargs: Дополнительные именованные аргументы для всех процессоров входа.
            Передаются в каждый processor как `**kwargs`.
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
    self, item: MealyStateString | MealyState[InputType, OutputType]
  ) -> tuple[str, MealyState[InputType, OutputType]]:
    name: str
    state: MealyState[InputType, OutputType]

    if isinstance(item, str):
      name = item
      state = MealyState[InputType, OutputType](name, {})

    elif isinstance(item, MealyState):
      name = item.name
      state = item

    else:
      raise TypeError(f"Expected `str` or `MealyState`, got `{type(item).__name__}`")

    return (name, state)

  # MARK: Transitions
  # --------------------------------------------------------------------------------------

  def add_transition(
    self,
    source_state: str,
    target_state: str,
    trans_condition: TransConditionProtocol[InputType],
    output_function: OutputFunctionProtocol[OutputType],
    input_processor: InputProcessorProtocol[InputType],
    replace: bool = False,
  ) -> None:
    """
    Добавляет переход.

    Если исходное или целевое состояние не существуют, они создаются автоматически.

    Args:
      source_state: Имя исходного состояния.
      target_state: Имя целевого состояния.
      trans_condition: Функция-условие.
      output_function: Функция вычисления выхода.
      input_processor: Функция обработки входа.
      replace: Если `True` и переход уже существует, он заменяется.
        Если `False` и переход существует, вызывается `ValueError`.

    Raises:
      `ValueError`: Если переход уже существует и `replace=False`.
    """

    self._add_transition(
      source_state,
      target_state,
      trans_condition,
      output_function,
      input_processor,
      replace,
    )

  # --------------------------------------------------------------------------------------

  def add_transition_entity(
    self,
    transition: MealyTransitionTuple[InputType, OutputType]
    | MealyTransition[InputType, OutputType],
    replace: bool = False,
  ) -> None:
    """
    Добавляет переход из готового объекта или кортежа.

    Args:
        transition: Объект MealyTransition или кортеж из 5 элементов.
        replace: Заменять существующий переход или нет.

    Raises:
      `ValueError`: Если переход уже существует и `replace=False`.
      `TypeError`: Если передан неподдерживаемый тип.
    """

    if isinstance(transition, MealyTransition):
      self._add_transition_entity(transition, replace)

    elif isinstance(transition, tuple):
      self._add_transition_tuple(transition, 5, replace)

    else:
      raise TypeError(f"Expected {MealyTransition} or tuple, got {type(transition)}")

  # --------------------------------------------------------------------------------------

  def _ensure_state_exists(self, state_name: str) -> None:
    if state_name not in self._states:
      self._states[state_name] = MealyState[InputType, OutputType](state_name, {})

  # --------------------------------------------------------------------------------------

  def _create_transition(
    self,
    source_state: str,
    target_state: str,
    trans_condition: TransConditionProtocol[InputType],
    output_function: OutputFunctionProtocol[OutputType] | None,
    input_processor: InputProcessorProtocol[InputType],
  ) -> MealyTransition[InputType, OutputType]:
    """
    Создаёт объект перехода.

    Args:
      source_state: Имя исходного состояния.
      target_state: Имя целевого состояния.
      trans_condition: Функция-условие перехода.
      output_function: Функция вычисления выхода.
      input_processor: Функция обработки входа.

    Returns:
      Объект `MealyTransition`.

    Raises:
      `ValueError`: Если `output_function` равен `None`.
    """

    if output_function is None:
      raise ValueError("`output_function` cannot be `None`")

    return MealyTransition(
      source_state=source_state,
      target_state=target_state,
      trans_condition=trans_condition,
      output_function=output_function,
      input_processor=input_processor,
    )
