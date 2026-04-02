"""
Модуль с классом автомата Мура.

Предоставляет API для создания, настройки и выполнения автомата.
"""

from .._base.machine import BaseMachine
from ..utils.protocols import StopConditionProtocol
from ..utils.types import UNSET_TYPE, Kwargs
from ._entity_api import MooreEntityApi
from .state import MooreState
from .transition import MooreTransition
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

    MooreEntityApi.__init__(
      self,
      states,
      transitions,
      initial_state,
      initial_output,
      initial_input,
      stop_condition,
      stop_condition_kwargs,
      condition_kwargs,
      function_kwargs,
      processor_kwargs,
    )

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
    """
    Выполняет функцию выхода текущего состояния.

    Returns:
      Результат выполнения функции выхода.

    Raises:
      `RuntimeError`: Если текущее состояние или выход не установлены.
    """

    if isinstance(self._current_state, UNSET_TYPE):
      raise RuntimeError("Current state not set")

    if isinstance(self._current_output, UNSET_TYPE):
      raise RuntimeError("Current output not set")

    return self._current_state.execute(self._current_output, self._function_kwargs)

  # --------------------------------------------------------------------------------------

  def _execute_transition(
    self, transition: MooreTransition[InputType], state_output: OutputType | None
  ) -> OutputType:
    """
    Выполняет переход. В автомате Мура выходное значение определяется состоянием,
    поэтому переход возвращает то же значение, что и состояние.

    Args:
      transition: Объект перехода.
      state_output: Выходное значение, полученное от состояния.

    Returns:
      Выходное значение состояния.

    Raises:
      `RuntimeError`: Если `state_output` равен `None`.
    """

    if state_output is None:
      raise RuntimeError("Moore machine: state_output cannot be None")

    return state_output
