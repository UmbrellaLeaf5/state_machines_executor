from ..utils.protocols import (
  InputProcessorProtocol,
  OutputFunctionProtocol,
  TransConditionProtocol,
)


type MooreTransitionTuple[InputType] = tuple[
  str,
  str,
  TransConditionProtocol[InputType],
  InputProcessorProtocol[InputType],
]


type MooreStateTuple[OutputType] = tuple[str, OutputFunctionProtocol[OutputType]]
