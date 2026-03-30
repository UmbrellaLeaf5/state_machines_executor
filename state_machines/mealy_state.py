from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


Kwargs = dict[str, Any]


class MealyConditionProtocol[InputType](Protocol):
  def __call__(self, input: InputType, *args: Any, **kwargs: Any) -> bool: ...


class MealyFunctionProtocol[OutputType](Protocol):
  def __call__(
    self, previous_output: OutputType, *args: Any, **kwargs: Any
  ) -> OutputType: ...


class MealyInputProcessorProtocol[InputType](Protocol):
  def __call__(self, input: InputType, *args: Any, **kwargs: Any) -> InputType: ...


@dataclass
class MealyTransition[InputType, OutputType]:
  source_state: str
  target_state: str

  condition: MealyConditionProtocol[InputType]
  function: MealyFunctionProtocol[OutputType]
  input_processor: MealyInputProcessorProtocol[InputType]

  def is_transferable(
    self, input: InputType, condition_kwargs: Kwargs | None = None
  ) -> bool:
    if condition_kwargs is None:
      condition_kwargs = {}

    return self.condition(input, **condition_kwargs)

  def execute(
    self, previous_output: OutputType, function_kwargs: Kwargs | None = None
  ) -> OutputType:
    if function_kwargs is None:
      function_kwargs = {}

    return self.function(previous_output, **function_kwargs)

  def process_input(
    self, input: InputType, processor_kwargs: Kwargs | None = None
  ) -> InputType:
    if processor_kwargs is None:
      processor_kwargs = {}

    return self.input_processor(input, **processor_kwargs)


@dataclass
class MealyState[InputType, OutputType]:
  name: str

  transitions: dict[str, MealyTransition[InputType, OutputType]]

  def add_transition(self, transition: MealyTransition[InputType, OutputType]):
    if transition.source_state != self.name:
      raise ValueError(
        f"Invalid transition.source_state: {transition.source_state} != {self.name}"
      )

    self.transitions[transition.target_state] = transition

  def get_available_transitions(
    self, input: InputType, condition_kwargs: Kwargs | None = None
  ) -> list[MealyTransition[InputType, OutputType]]:
    if condition_kwargs is None:
      condition_kwargs = {}

    return [
      transition
      for transition in self.transitions.values()
      if transition.is_transferable(input, condition_kwargs)
    ]
