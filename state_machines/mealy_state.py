from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


Kwargs = dict[str, Any]


class MealyConditionProtocol[InputType](Protocol):
  def __call__(self, input: InputType, *args: Any, **kwargs: Any) -> bool: ...


class MealyFunctionProtocol[ResultType](Protocol):
  def __call__(
    self, previous_result: ResultType, *args: Any, **kwargs: Any
  ) -> ResultType: ...


class MealyInputProcessorProtocol[InputType](Protocol):
  def __call__(self, input: InputType, *args: Any, **kwargs: Any) -> InputType: ...


@dataclass
class MealyStateTransitionInfo[InputType, ResultType]:
  state_name: str

  condition: MealyConditionProtocol[InputType]
  function: MealyFunctionProtocol[ResultType]
  input_processor: MealyInputProcessorProtocol[InputType]

  def is_transferable(
    self, input: InputType, condition_kwargs: Kwargs | None = None
  ) -> bool:
    if condition_kwargs is None:
      condition_kwargs = {}

    return self.condition(input, **condition_kwargs)

  def execute(
    self, previous_result: ResultType, function_kwargs: Kwargs | None = None
  ) -> ResultType:
    if function_kwargs is None:
      function_kwargs = {}

    return self.function(previous_result, **function_kwargs)

  def process_input(
    self, input: InputType, processor_kwargs: Kwargs | None = None
  ) -> InputType:
    if processor_kwargs is None:
      processor_kwargs = {}

    return self.input_processor(input, **processor_kwargs)


@dataclass
class MealyState[InputType, ResultType]:
  name: str

  transitions: dict[str, MealyStateTransitionInfo[InputType, ResultType]]

  def add_transition(self, transition: MealyStateTransitionInfo[InputType, ResultType]):
    self.transitions[transition.state_name] = transition

  def get_available_transitions(
    self, input: InputType, condition_kwargs: Kwargs | None = None
  ) -> list[MealyStateTransitionInfo[InputType, ResultType]]:
    if condition_kwargs is None:
      condition_kwargs = {}

    return [
      transition
      for transition in self.transitions.values()
      if transition.is_transferable(input, condition_kwargs)
    ]
