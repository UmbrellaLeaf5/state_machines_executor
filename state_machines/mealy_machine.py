"""
Модуль с классом автомата Мили.

Предоставляет API для создания, настройки и выполнения автомата.
"""

import warnings

from state_machines.mealy_state import (
  Kwargs,
  MealyConditionProtocol,
  MealyFunctionProtocol,
  MealyInputProcessorProtocol,
  MealyState,
  MealyTransition,
)
from state_machines.mealy_step import MealyStepData, MealyStepReason, MealyStepResult


class _UNSET:
  """Сентинель для обозначения 'значение не установлено'."""

  pass


_UNSET_VAL = _UNSET()

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


class MealyMachine[InputType, OutputType]:
  """
  Автомат Мили.

  Позволяет задать состояния, переходы, выполнять шаги и получать результаты.
  """

  # MARK: Fields
  # --------------------------------------------------------------------------------------

  __states: dict[str, MealyState[InputType, OutputType]]
  __results: list[MealyStepResult[InputType, OutputType]]

  __current_state: MealyState[InputType, OutputType] | _UNSET
  __current_output: OutputType | _UNSET
  __current_input: InputType | _UNSET

  __condition_kwargs: Kwargs
  __function_kwargs: Kwargs
  __processor_kwargs: Kwargs

  __stop_condition: MealyConditionProtocol[InputType] | None
  __stop_condition_kwargs: Kwargs

  # MARK: Init
  # --------------------------------------------------------------------------------------

  def __init__(
    self,
    transitions: list[
      tuple[
        str,
        str,
        MealyConditionProtocol[InputType],
        MealyFunctionProtocol[OutputType],
        MealyInputProcessorProtocol[InputType],
      ]
    ]
    | None = None,
    *,
    initial_state: str | None = None,
    initial_output: OutputType | None = None,
    initial_input: InputType | None = None,
    stop_condition: MealyConditionProtocol[InputType] | None = None,
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
      transitions: Список переходов. Каждый переход - кортеж из пяти элементов:
          (source_state, target_state, condition, function, processor).
          - source_state: имя исходного состояния
          - target_state: имя целевого состояния
          - condition: функция-условие (арг.: input, возвращает bool)
          - function: функция вычисл. выхода (арг.: previous_output, возвращает output)
          - processor: функция обработки входа (арг.: input, возвращает новый input)

      initial_state: Имя начального состояния. Если указан, должны быть также указаны
        `initial_output` и `initial_input`.

      initial_output: Нач. выходное значение. Используется вместе с `initial_state`.

      initial_input: Начальное входное значение. Используется вместе с `initial_state`.

      stop_condition: Функция-условие остановки. Вызывается перед каждым шагом,
        принимает текущий вход и возвращает `True` для остановки.

      stop_condition_kwargs: Дополнительные именованные аргументы для `stop_condition`.
        Передаются в функцию как `**kwargs`.

      condition_kwargs: Дополнительные именованные аргументы для всех условий переходов.
        Передаются в каждую condition как `**kwargs`.

      function_kwargs: Доп. именованные аргументы для всех функций вычисления выхода.
        Передаются в каждую function как `**kwargs`.

      processor_kwargs: Дополнительные именованные аргументы для всех процессоров входа.
        Передаются в каждый processor как `**kwargs`.
    """

    self.__states = {}
    self.__results = []

    self.__current_state = _UNSET_VAL
    self.__current_output = _UNSET_VAL
    self.__current_input = _UNSET_VAL

    self.__condition_kwargs = {}
    self.__function_kwargs = {}
    self.__processor_kwargs = {}

    self.__stop_condition = None
    self.__stop_condition_kwargs = {}

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
      self.update_current_data(initial_state, initial_output, initial_input)

  # MARK: Reset Machine
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

  # MARK: States
  # --------------------------------------------------------------------------------------

  def get_state_names(self) -> list[str]:
    """Возвращает список имён всех состояний (копия)."""

    return list(self.__states.keys())

  def get_states_amount(self) -> int:
    """Возвращает количество состояний."""

    return len(self.__states)

  # --------------------------------------------------------------------------------------
  # !: entity + entities

  def add_state(self, state: MealyState[InputType, OutputType]) -> None:
    """
    Добавляет состояние.

    Args:
      state: Объект состояния.

    Raises:
      `ValueError`: Если состояние с таким именем уже существует.
    """

    if state.name in self.__states:
      raise ValueError(f"State '{state.name}' already exists")

    self.__states[state.name] = state

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

    if state_name not in self.__states:
      raise KeyError(f"State '{state_name}' is not found")

    if (
      not isinstance(self.__current_state, _UNSET)
      and self.__current_state.name == state_name
    ):
      warnings.warn(
        f"Removing current state '{state_name}', machine reset",
        UserWarning,
        stacklevel=2,
      )
      self.clear_current_data()

    if cleanup_transitions:
      for state in self.__states.values():
        if state_name in state.transitions:
          state.remove_transition(state_name)

      self.__states[state_name].transitions.clear()

    self.__states.pop(state_name)

  def set_states(self, states: list[str | MealyState[InputType, OutputType]]) -> None:
    """
    Заменяет все состояния новыми.

    Args:
      states: Список имён (строк) или объектов `MealyState`.
    """

    self.clear_states()
    self.update_states(states)

  def update_states(self, states: list[str | MealyState[InputType, OutputType]]) -> None:
    """
    Добавляет несколько состояний атомарно.

    Args:
      states: Список имён (строк) или объектов `MealyState`.

    Raises:
      `TypeError`: При неверном типе элемента.
      `ValueError`: При дубликате имени в списке или если состояние уже существует.
    """

    items: list[tuple[str, MealyState[InputType, OutputType]]] = []
    seen_names: set[str] = set()

    for item in states:
      if isinstance(item, str):
        name = item
        state = MealyState[InputType, OutputType](name, {})

      elif isinstance(item, MealyState):
        name = item.name
        state = item

      else:
        raise TypeError(f"Expected `str` or `MealyState`, got `{type(item).__name__}`")

      # проверяем дубликаты в списке
      if name in seen_names:
        raise ValueError(f"Duplicate state name in input: {name}")
      seen_names.add(name)

      # проверяем, что состояние не существует в автомате
      if name in self.__states:
        raise ValueError(f"State '{name}' already exists")

      items.append((name, state))

    for name, state in items:
      self.__states[name] = state

  def clear_states(self) -> None:
    """Удаляет все состояния."""

    self.__states.clear()

  # MARK: Transitions
  # --------------------------------------------------------------------------------------

  def get_state_transitions(
    self, state_name: str
  ) -> list[
    tuple[
      str,
      MealyConditionProtocol[InputType],
      MealyFunctionProtocol[OutputType],
      MealyInputProcessorProtocol[InputType],
    ]
  ]:
    """
    Возвращает список переходов из указанного состояния.

    Args:
      state_name: Имя состояния.

    Returns:
      Список кортежей `(target_state, condition, function, processor)`.

    Raises:
      `KeyError`: Если состояние не существует.
    """

    if state_name not in self.__states:
      raise KeyError(f"State '{state_name}' not found")

    state = self.__states[state_name]

    return [
      (
        target,
        trans.condition,
        trans.function,
        trans.input_processor,
      )
      for target, trans in state.transitions.items()
    ]

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

    if state_name not in self.__states:
      raise KeyError(f"State '{state_name}' not found")

    return len(self.__states[state_name].transitions)

  def get_all_transitions(
    self,
  ) -> list[
    tuple[
      str,
      str,
      MealyConditionProtocol[InputType],
      MealyFunctionProtocol[OutputType],
      MealyInputProcessorProtocol[InputType],
    ]
  ]:
    """
    Возвращает список всех переходов в автомате.

    Returns:
      Список кортежей `(source_state, target_state, condition, function, processor)`.
    """

    return [
      (state_name, target, trans.condition, trans.function, trans.input_processor)
      for state_name, state in self.__states.items()
      for target, trans in state.transitions.items()
    ]

  def get_all_transitions_amount(self) -> int:
    """Возвращает общее количество переходов во всех состояниях."""

    return sum(len(state.transitions) for state in self.__states.values())

  # --------------------------------------------------------------------------------------
  # !: entity + entities

  def add_transition(
    self,
    source_state: str,
    target_state: str,
    condition: MealyConditionProtocol[InputType],
    function: MealyFunctionProtocol[OutputType],
    input_processor: MealyInputProcessorProtocol[InputType],
    replace: bool = False,
  ) -> None:
    """
    Добавляет переход.

    Если исходное или целевое состояние не существуют, они создаются автоматически.

    Args:
      source_state: Имя исходного состояния.
      target_state: Имя целевого состояния.
      condition: Функция-условие.
      function: Функция вычисления выхода.
      input_processor: Функция обработки входа.
      replace: Если `True` и переход уже существует, он заменяется.
               Если `False` и переход существует, вызывается `ValueError`.

    Raises:
      ValueError: Если переход уже существует и `replace=False`.
    """

    # создаём исходное состояние, если его нет
    if source_state not in self.__states:
      self.__states[source_state] = MealyState[InputType, OutputType](source_state, {})

    # создаём целевое состояние, если его нет
    if target_state not in self.__states:
      self.__states[target_state] = MealyState[InputType, OutputType](target_state, {})

    transition = MealyTransition(
      source_state=source_state,
      target_state=target_state,
      condition=condition,
      function=function,
      input_processor=input_processor,
    )

    source = self.__states[source_state]

    if source.has_transition(target_state):
      if not replace:
        raise ValueError(
          f"Transition from '{source_state}' to '{target_state}' already exists. "
          "Use `replace=True` to replace it."
        )

      source.replace_transition(transition)

    else:
      source.add_transition(transition)

  def remove_transition(self, source_state: str, target_state: str) -> None:
    """
    Удаляет переход.

    Args:
        source_state: Имя исходного состояния.
        target_state: Имя целевого состояния.

    Raises:
        `KeyError`: Если исходное состояние не существует или переход не найден.
    """

    if source_state not in self.__states:
      raise KeyError(f"State '{source_state}' is not found")

    state = self.__states[source_state]

    if target_state not in state.transitions:
      raise KeyError(f"Transition from '{source_state}' to '{target_state}' is not found")

    state.remove_transition(target_state)

  def set_transitions(
    self,
    transitions: list[
      tuple[
        str,
        str,
        MealyConditionProtocol[InputType],
        MealyFunctionProtocol[OutputType],
        MealyInputProcessorProtocol[InputType],
      ]
    ],
  ) -> None:
    """
    Заменяет все переходы новыми.

    Args:
        transitions: Список переходов `(source, target, condition, function, processor)`.
    """

    self.clear_transitions()
    self.update_transitions(transitions)

  def update_transitions(
    self,
    transitions: list[
      tuple[
        str,
        str,
        MealyConditionProtocol[InputType],
        MealyFunctionProtocol[OutputType],
        MealyInputProcessorProtocol[InputType],
      ]
    ],
  ) -> None:
    """
    Добавляет несколько переходов.

    Args:
        transitions: Список переходов `(source, target, condition, function, processor)`.
    """

    for source, target, cond, func, proc in transitions:
      self.add_transition(source, target, cond, func, proc)

  def clear_transitions(self) -> None:
    """Удаляет все переходы из всех состояний."""

    for state in self.__states.values():
      state.transitions.clear()

  # MARK: Current data
  # --------------------------------------------------------------------------------------

  def get_current_state_name(self) -> str | None:
    """Возвращает имя текущего состояния или `None`, если оно не установлено."""

    if isinstance(self.__current_state, _UNSET):
      return None

    return self.__current_state.name

  def get_current_output(self) -> OutputType | None:
    """Возвращает текущее выходное значение или `None`, если оно не установлено."""

    if isinstance(self.__current_output, _UNSET):
      return None

    return self.__current_output

  def get_current_input(self) -> InputType | None:
    """Возвращает текущее входное значение или `None`, если оно не установлено."""

    if isinstance(self.__current_input, _UNSET):
      return None

    return self.__current_input

  def is_ready(self) -> bool:
    """Проверяет, что автомат готов к запуску (установлены состояние, выход и вход)."""

    return not (
      isinstance(self.__current_state, _UNSET)
      or isinstance(self.__current_output, _UNSET)
      or isinstance(self.__current_input, _UNSET)
    )

  # --------------------------------------------------------------------------------------
  # !: entities

  def set_current_data(
    self,
    state_name: str,
    output: OutputType,
    input: InputType,
  ) -> None:
    """
    Устанавливает все компоненты текущего состояния.

    Args:
        state_name: Имя состояния.
        output: Выходное значение.
        input: Входное значение.
    """

    self.clear_current_data()
    self.update_current_data(state_name, output, input)

  def update_current_data(
    self,
    state_name: str | None,
    output: OutputType | None,
    input: InputType | None,
  ) -> None:
    """
    Частично обновляет текущие данные.

    Можно обновить только состояние, только выход, только вход или любую комбинацию.

    Примечание: Для `is_ready()` требуются все три компонента.
    Если обновить только выход или вход без состояния, автомат не будет готов к запуску.

    Args:
      state_name: Имя состояния (или `None`, чтобы не обновлять).
      output: Выходное значение (или `None`, чтобы не обновлять).
      input: Входное значение (или `None`, чтобы не обновлять).

    Raises:
      `KeyError`: Если `state_name` передан, но состояние не существует.
    """

    if state_name is not None:
      if state_name not in self.__states:
        raise KeyError(f"State '{state_name}' not found")

      self.__current_state = self.__states[state_name]

    if output is not None:
      self.__current_output = output

    if input is not None:
      self.__current_input = input

  def clear_current_data(self) -> None:
    """Сбрасывает текущие данные в состояние 'не установлено'"""

    self.__current_state = _UNSET_VAL
    self.__current_output = _UNSET_VAL
    self.__current_input = _UNSET_VAL

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
      self.__condition_kwargs.update(condition_kwargs)

    if function_kwargs is not None:
      self.__function_kwargs.update(function_kwargs)

    if processor_kwargs is not None:
      self.__processor_kwargs.update(processor_kwargs)

  def clear_common_kwargs(self) -> None:
    """Очищает все common kwargs."""

    self.__condition_kwargs = {}
    self.__function_kwargs = {}
    self.__processor_kwargs = {}

  # MARK: Stop condition
  # --------------------------------------------------------------------------------------
  # !: entity

  def add_stop_condition(
    self,
    stop_condition: MealyConditionProtocol[InputType],
    stop_condition_kwargs: Kwargs | None = None,
  ) -> None:
    """
    Устанавливает условие остановки.

    Args:
      stop_condition: Функция, принимающая вход и возвращающая True для остановки.
      stop_condition_kwargs: Дополнительные аргументы для `stop_condition`.
    """

    if stop_condition_kwargs is None:
      stop_condition_kwargs = {}

    self.__stop_condition = stop_condition
    self.__stop_condition_kwargs = stop_condition_kwargs

  def remove_stop_condition(self) -> None:
    """Удаляет условие остановки."""

    self.__stop_condition = None
    self.__stop_condition_kwargs = {}

  # MARK: Run
  # --------------------------------------------------------------------------------------

  def run_once(self) -> MealyStepResult[InputType, OutputType]:
    """
    Выполняет один шаг автомата.

    Returns:
      Результат шага с указанием причины завершения и данными (если успешно).

    Raises:
      `RuntimeError`: Если текущие данные не установлены.
      `ValueError`: Если найдено несколько доступных переходов (неоднозначность).
      `KeyError`: Если целевое состояние не существует.
    """

    if isinstance(self.__current_state, _UNSET):
      raise RuntimeError("Current state not set")

    if isinstance(self.__current_output, _UNSET):
      raise RuntimeError("Current output not set")

    if isinstance(self.__current_input, _UNSET):
      raise RuntimeError("Current input not set")

    # IMP: идеологически:
    # if not self.is_ready():
    #   raise RuntimeError(...)
    # (но нужно сужение типов, поэтому не используем)

    if self.__stop_condition and self.__stop_condition(
      self.__current_input, **self.__stop_condition_kwargs
    ):
      return MealyStepResult(reason=MealyStepReason.STOP_CONDITION)

    available_transitions = self.__current_state.get_available_transitions(
      self.__current_input, self.__condition_kwargs
    )

    if not available_transitions:
      return MealyStepResult(reason=MealyStepReason.NO_TRANSITION)

    if len(available_transitions) > 1:
      raise RuntimeError(
        f"Ambiguous transition: {[t.target_state for t in available_transitions]}"
      )

    transition = available_transitions[0]

    output = transition.execute(self.__current_output, self.__function_kwargs)

    processed_input = transition.process_input(
      self.__current_input, self.__processor_kwargs
    )

    target_state = self.__states.get(transition.target_state)
    if target_state is None:
      raise KeyError(
        f"Target state '{transition.target_state}' not found in machine states"
      )

    self.__current_state = target_state
    self.__current_output = output
    self.__current_input = processed_input

    mealy_step = MealyStepResult(
      reason=MealyStepReason.SUCCESS, data=(processed_input, output)
    )
    self.__results.append(mealy_step)
    return mealy_step

  # --------------------------------------------------------------------------------------

  def run_all(
    self, clear_before_run: bool = False
  ) -> list[MealyStepResult[InputType, OutputType]]:
    """
    Выполняет автомат до остановки (по условию или отсутствию переходов).

    Args:
      clear_before_run: Если `True`, очищает историю результатов перед запуском.
                        Если `False`, добавляет новые шаги к существующим.

    Returns:
      Список успешных шагов выполнения (копия).
    """

    if clear_before_run:
      self.clear_results()

    while True:
      step_result = self.run_once()

      if step_result.reason != MealyStepReason.SUCCESS:
        break

    return self.get_results()

  # MARK: Results
  # --------------------------------------------------------------------------------------

  def get_results(self) -> list[MealyStepResult[InputType, OutputType]]:
    """Возвращает копию списка всех успешных шагов."""

    return self.__results.copy()

  def get_results_data(self) -> list[MealyStepData[InputType, OutputType]]:
    """Возвращает копии данных всех успешных шагов."""

    return [MealyStepData(step.data.input, step.data.output) for step in self.__results]

  def get_results_tuple(self) -> list[tuple[InputType | None, OutputType | None]]:
    """Возвращает список кортежей `(input, output)` для всех успешных шагов."""

    return [(step.data.input, step.data.output) for step in self.__results]

  def get_only_results(self) -> list[OutputType | None]:
    """Возвращает список выходных значений всех успешных шагов."""

    return [step.data.output for step in self.__results]

  def get_final_result(self) -> OutputType | None:
    """Возвращает выходное значение последнего успешного шага или `None`."""

    if not self.__results:
      return None

    return self.__results[-1].data.output

  def clear_results(self) -> None:
    """Очищает историю результатов выполнения."""

    self.__results.clear()
