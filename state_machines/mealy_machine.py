from state_machines.mealy_state import Kwargs, MealyConditionProtocol, MealyState


class MealyMachine[InputType, ResultType]:
  states: dict[str, MealyState[InputType, ResultType]]
  results: list[tuple[InputType, ResultType]]

  current_state: MealyState[InputType, ResultType] | None
  current_result: ResultType | None
  current_input: InputType | None

  condition_kwargs: Kwargs
  function_kwargs: Kwargs
  processor_kwargs: Kwargs

  stop_condition: MealyConditionProtocol[InputType] | None
  stop_condition_kwargs: Kwargs

  def __init__(self):
    self.states = {}
    self.results = []

    self.current_state = None
    self.current_result = None
    self.current_input = None

    self.condition_kwargs = {}
    self.function_kwargs = {}
    self.processor_kwargs = {}

    self.stop_condition = None
    self.stop_condition_kwargs = {}

  def reset(self):
    self.current_state = None
    self.current_result = None
    self.current_input = None

    self.results.clear()

  def add_state(self, state: MealyState[InputType, ResultType]):
    self.states[state.name] = state

  def set_initial_state(
    self,
    state_name: str,
    initial_result: ResultType | None = None,
    initial_input: InputType | None = None,
  ):
    if state_name not in self.states:
      raise KeyError(f"State '{state_name}' not found")

    self.current_state = self.states[state_name]
    self.current_result = initial_result
    self.current_input = initial_input

  def set_kwargs(
    self,
    condition_kwargs: Kwargs | None = None,
    function_kwargs: Kwargs | None = None,
    processor_kwargs: Kwargs | None = None,
  ):
    if condition_kwargs is not None:
      self.condition_kwargs = condition_kwargs

    if function_kwargs is not None:
      self.function_kwargs = function_kwargs

    if processor_kwargs is not None:
      self.processor_kwargs = processor_kwargs

  def set_stop_condition(
    self,
    stop_condition: MealyConditionProtocol,
    stop_condition_kwargs: Kwargs | None = None,
  ):
    if stop_condition_kwargs is None:
      stop_condition_kwargs = {}

    self.stop_condition = stop_condition
    self.stop_condition_kwargs = stop_condition_kwargs

  def run_once(self) -> tuple[InputType, ResultType] | None:
    if self.current_state is None:
      raise RuntimeError("Current state not set")

    if self.current_result is None:
      raise RuntimeError("Current result not set")

    if self.current_input is None:
      raise RuntimeError("Current input not set")

    if self.stop_condition and self.stop_condition(
      self.current_input, **self.stop_condition_kwargs
    ):
      return None

    available_transitions = self.current_state.get_available_transitions(
      self.current_input, self.condition_kwargs
    )

    if not available_transitions:
      return None

    if len(available_transitions) > 1:
      raise RuntimeError(
        f"Ambiguous transition: {[t.state_name for t in available_transitions]}"
      )

    transition = available_transitions[0]

    result = transition.execute(self.current_result, self.function_kwargs)

    processed_input = transition.process_input(self.current_input, self.processor_kwargs)

    self.current_state = self.states[transition.state_name]
    self.current_result = result
    self.current_input = processed_input

    self.results.append((processed_input, result))
    return (processed_input, result)

  def run_all(self) -> list[tuple[InputType, ResultType]]:
    while True:
      result = self.run_once()

      if result is None:
        break

    return self.results
