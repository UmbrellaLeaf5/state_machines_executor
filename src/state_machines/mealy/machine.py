"""
Модуль с классом автомата Мили.

Предоставляет API для создания, настройки и выполнения автомата.
"""

from .._base.machine import BaseMachine
from ..utils.protocols import StopConditionProtocol
from ..utils.types import UNSET_TYPE, Kwargs
from ._entity_api import MealyEntityApi
from .state import MealyState
from .transition import MealyTransition
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

    MealyEntityApi.__init__(
      self,
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
