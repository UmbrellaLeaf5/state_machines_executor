from state_machines.mealy_state import Kwargs, MealyConditionProtocol, MealyState


class _UNSET:
  pass


_UNSET_VAL = _UNSET()


class MealyMachine[InputType, ResultType]:
  __states: dict[str, MealyState[InputType, ResultType]]
  __results: list[tuple[InputType, ResultType]]

  __current_state: MealyState[InputType, ResultType] | _UNSET
  __current_result: ResultType | _UNSET
  __current_input: InputType | _UNSET

  __condition_kwargs: Kwargs
  __function_kwargs: Kwargs
  __processor_kwargs: Kwargs

  __stop_condition: MealyConditionProtocol[InputType] | None
  __stop_condition_kwargs: Kwargs

  def __init__(self):
    self.__states = {}
    self.__results = []

    self.__current_state = _UNSET_VAL
    self.__current_result = _UNSET_VAL
    self.__current_input = _UNSET_VAL

    self.__condition_kwargs = {}
    self.__function_kwargs = {}
    self.__processor_kwargs = {}

    self.__stop_condition = None
    self.__stop_condition_kwargs = {}

  def reset(self):
    self.__current_state = _UNSET_VAL
    self.__current_result = _UNSET_VAL
    self.__current_input = _UNSET_VAL

    self.__results.clear()

  def add_state(self, state: MealyState[InputType, ResultType]):
    self.__states[state.name] = state

  def set_initial_state(
    self,
    state_name: str,
    initial_result: ResultType,
    initial_input: InputType,
  ):
    if state_name not in self.__states:
      raise KeyError(f"State '{state_name}' not found")

    self.__current_state = self.__states[state_name]
    self.__current_result = initial_result
    self.__current_input = initial_input

  def set_kwargs(
    self,
    condition_kwargs: Kwargs | None = None,
    function_kwargs: Kwargs | None = None,
    processor_kwargs: Kwargs | None = None,
  ):
    if condition_kwargs is not None:
      self.__condition_kwargs = condition_kwargs

    if function_kwargs is not None:
      self.__function_kwargs = function_kwargs

    if processor_kwargs is not None:
      self.__processor_kwargs = processor_kwargs

  def set_stop_condition(
    self,
    stop_condition: MealyConditionProtocol[InputType],
    stop_condition_kwargs: Kwargs | None = None,
  ):
    if stop_condition_kwargs is None:
      stop_condition_kwargs = {}

    self.__stop_condition = stop_condition
    self.__stop_condition_kwargs = stop_condition_kwargs

  def run_once(self) -> tuple[InputType, ResultType] | None:
    if isinstance(self.__current_state, _UNSET):
      raise RuntimeError("Current state not set")

    if isinstance(self.__current_result, _UNSET):
      raise RuntimeError("Current result not set")

    if isinstance(self.__current_input, _UNSET):
      raise RuntimeError("Current input not set")

    if self.__stop_condition and self.__stop_condition(
      self.__current_input, **self.__stop_condition_kwargs
    ):
      return None

    available_transitions = self.__current_state.get_available_transitions(
      self.__current_input, self.__condition_kwargs
    )

    if not available_transitions:
      return None

    if len(available_transitions) > 1:
      raise RuntimeError(
        f"Ambiguous transition: {[t.state_name for t in available_transitions]}"
      )

    transition = available_transitions[0]

    result = transition.execute(self.__current_result, self.__function_kwargs)

    processed_input = transition.process_input(
      self.__current_input, self.__processor_kwargs
    )

    target_state = self.__states.get(transition.state_name)
    if target_state is None:
      raise KeyError(
        f"Target state '{transition.state_name}' not found in machine states"
      )

    self.__current_state = target_state
    self.__current_result = result
    self.__current_input = processed_input

    self.__results.append((processed_input, result))
    return (processed_input, result)

  def run_all(self) -> list[tuple[InputType, ResultType]]:
    while True:
      result = self.run_once()

      if result is None:
        break

    return self.__results
