from ..utils.protocols import (
  InputProcessorProtocol,
  OutputFunctionProtocol,
  TransConditionProtocol,
)


type MealyTransitionTuple[InputType, OutputType] = tuple[
  str,
  str,
  TransConditionProtocol[InputType],
  OutputFunctionProtocol[OutputType],
  InputProcessorProtocol[InputType],
]

type MealyStateString = str
