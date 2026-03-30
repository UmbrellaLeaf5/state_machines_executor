from state_machines.mealy_state import Kwargs, MealyConditionProtocol, MealyState
from state_machines.mealy_step import MealyStepData, MealyStepReason, MealyStepResult


class _UNSET:
  pass


_UNSET_VAL = _UNSET()


class MealyMachine[InputType, OutputType]:
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

  def __init__(self):
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

  def reset(self):
    self.__current_state = _UNSET_VAL
    self.__current_output = _UNSET_VAL
    self.__current_input = _UNSET_VAL

    self.__results.clear()

  def add_state(self, state: MealyState[InputType, OutputType]):
    self.__states[state.name] = state

  def set_initial_state(
    self,
    state_name: str,
    initial_output: OutputType,
    initial_input: InputType,
  ):
    if state_name not in self.__states:
      raise KeyError(f"State '{state_name}' is not found")

    self.__current_state = self.__states[state_name]
    self.__current_output = initial_output
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

  def run_once(self) -> MealyStepResult[InputType, OutputType]:
    if isinstance(self.__current_state, _UNSET):
      raise RuntimeError("Current state is not set")

    if isinstance(self.__current_output, _UNSET):
      raise RuntimeError("Current output is not set")

    if isinstance(self.__current_input, _UNSET):
      raise RuntimeError("Current input is not set")

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
        f"Target state '{transition.target_state}' is not found in machine states"
      )

    self.__current_state = target_state
    self.__current_output = output
    self.__current_input = processed_input

    mealy_step = MealyStepResult(
      reason=MealyStepReason.SUCCESS, data=(processed_input, output)
    )
    self.__results.append(mealy_step)
    return mealy_step

  def run_all(self) -> list[MealyStepResult[InputType, OutputType]]:
    while True:
      step_result = self.run_once()

      if step_result.reason != MealyStepReason.SUCCESS:
        break

    return self.__results

  def get_results(self) -> list[MealyStepResult[InputType, OutputType]]:
    return self.__results

  def get_results_data(self) -> list[MealyStepData[InputType, OutputType]]:
    return [step.data for step in self.__results]

  def get_results_tuple(self) -> list[tuple[InputType | None, OutputType | None]]:
    return [(step.data.input, step.data.output) for step in self.__results]

  def get_only_results(self) -> list[OutputType | None]:
    return [step.data.output for step in self.__results]

  def get_final_result(self) -> OutputType | None:
    if not self.__results:
      return None

    return self.__results[-1].data.output
